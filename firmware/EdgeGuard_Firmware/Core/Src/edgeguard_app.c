/* EdgeGuard AI - application logic, independent of CubeMX-generated main.c.
 * UART and basic STM32 bring-up were demonstrated on the author's board.
 * MPU6050 I2C communication remains an open hardware integration issue.
 */
#include "edgeguard_app.h"
#include "mpu6050.h"
#include "motion_features.h"
#include "inference.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>

static I2C_HandleTypeDef *bus_i2c;
static UART_HandleTypeDef *link_uart;
static mpu6050_bus_t mpu_bus;
static feature_window_t feature_window;
static uint8_t sensor_ok;
static uint32_t next_sample_ms;
static uint32_t next_retry_ms;
static uint32_t led_toggle_ms;
static uint32_t dropped_reads;
static char line[160];

static void log_line(const char *s)
{
    if (!link_uart) return;
    HAL_UART_Transmit(link_uart, (uint8_t *)s, (uint16_t)strlen(s), 250u);
}

static int hal_mem_read(void *ctx, uint8_t address, uint8_t reg,
                        uint8_t *out, uint16_t count)
{
    return HAL_I2C_Mem_Read((I2C_HandleTypeDef *)ctx, (uint16_t)(address << 1),
                            reg, I2C_MEMADD_SIZE_8BIT, out, count, 100u) == HAL_OK ? 0 : -1;
}

static int hal_mem_write(void *ctx, uint8_t address, uint8_t reg,
                         const uint8_t *bytes, uint16_t count)
{
    return HAL_I2C_Mem_Write((I2C_HandleTypeDef *)ctx, (uint16_t)(address << 1),
                             reg, I2C_MEMADD_SIZE_8BIT, (uint8_t *)bytes,
                             count, 100u) == HAL_OK ? 0 : -1;
}

static uint32_t micro_score(float score)
{
    if (!(score >= 0.0f)) return 0u;
    if (score > 4000.0f) return 4000000000u;
    return (uint32_t)(score * 1000000.0f + 0.5f);
}

static void show_bus_diagnostics(void)
{
    /* BUSY flag can remain asserted on STM32F1 (see ST errata ES096).
     * Deliberately avoid automatically forcing recovery: electrical cause
     * has not been ruled out on this particular board. */
    (void)snprintf(line, sizeof(line),
       "I2C_DEBUG,state=0x%02X,error=0x%08lX,busy=%lu,SCL=%u,SDA=%u\r\n",
       (unsigned int)HAL_I2C_GetState(bus_i2c),
       (unsigned long)HAL_I2C_GetError(bus_i2c),
       (unsigned long)__HAL_I2C_GET_FLAG(bus_i2c, I2C_FLAG_BUSY),
       (unsigned int)HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_6),
       (unsigned int)HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_7));
    log_line(line);
}

static void attempt_sensor(void)
{
    uint8_t id = 0u;
    int result = mpu6050_init(&mpu_bus, &id);
    if (result == 0) {
        sensor_ok = 1u;
        dropped_reads = 0u;
        feature_window_reset(&feature_window);
        next_sample_ms = HAL_GetTick() + 10u;
        log_line(edgeguard_model_ready()
                 ? "READY,MPU6050,0x68,TINYML\r\n"
                 : "READY,MPU6050,0x68,HEURISTIC\r\n");
    } else {
        sensor_ok = 0u;
        next_retry_ms = HAL_GetTick() + 2000u;
        (void)snprintf(line, sizeof(line),
            "ERROR,MPU_INIT,code=%d,id=0x%02X\r\n",result,(unsigned)id);
        log_line(line);
        show_bus_diagnostics();
    }
}

void EdgeGuard_AppInit(I2C_HandleTypeDef *i2c, UART_HandleTypeDef *uart)
{
    bus_i2c = i2c;
    link_uart = uart;
    sensor_ok = 0u;
    dropped_reads = 0u;
    led_toggle_ms = HAL_GetTick();
    feature_window_reset(&feature_window);
    mpu_bus.context = i2c;
    mpu_bus.read = hal_mem_read;
    mpu_bus.write = hal_mem_write;
    mpu_bus.delay_ms = HAL_Delay;
    mpu_bus.address7 = MPU6050_ADDR;
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET); /* active-low LED */
    HAL_Delay(50);
    log_line("BOOT,EdgeGuardAI,CubeIDE,STM32F103,100Hz,window32\r\n");
    attempt_sensor();
}

void EdgeGuard_AppTick(void)
{
    uint32_t now = HAL_GetTick();
    if (!sensor_ok) {
        if ((uint32_t)(now - led_toggle_ms) >= 500u) {
            led_toggle_ms = now;
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        }
        if ((int32_t)(now - next_retry_ms) >= 0)
            attempt_sensor();
        HAL_Delay(1);
        return;
    }
    if ((int32_t)(now - next_sample_ms) < 0) {
        HAL_Delay(1);
        return;
    }
    next_sample_ms += 10u;
    if ((int32_t)(HAL_GetTick() - next_sample_ms) > 20)
        next_sample_ms = HAL_GetTick() + 10u;

    mpu6050_raw_t s;
    if (mpu6050_read(&mpu_bus, &s) != 0) {
        ++dropped_reads;
        feature_window_reset(&feature_window);
        if (dropped_reads == 1u || (dropped_reads % 25u) == 0u) {
            log_line("ERROR,I2C_READ\r\n");
            show_bus_diagnostics();
        }
        if (dropped_reads >= 25u) {
            sensor_ok = 0u;
            next_retry_ms = HAL_GetTick() + 2000u;
        }
        return;
    }
    dropped_reads = 0u;
    now = HAL_GetTick();
    (void)snprintf(line, sizeof(line), "S,%lu,%d,%d,%d,%d,%d,%d\r\n",
        (unsigned long)now, (int)s.ax, (int)s.ay, (int)s.az,
        (int)s.gx, (int)s.gy, (int)s.gz);
    log_line(line);

    feature_window_push(&feature_window, &s);
    float features[EDGEGUARD_FEATURES];
    if (feature_window_finish(&feature_window, features)) {
        float score = edgeguard_score(features);
        int alert = edgeguard_anomaly(score);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13,
                          alert ? GPIO_PIN_RESET : GPIO_PIN_SET);
        (void)snprintf(line, sizeof(line), "R,%lu,%s,%lu,%lu,%c\r\n",
            (unsigned long)now,
            edgeguard_model_ready() ? "TINYML" : "HEURISTIC",
            (unsigned long)micro_score(score),
            (unsigned long)micro_score(edgeguard_threshold()),
            alert ? 'A' : 'N');
        log_line(line);
    }
}
