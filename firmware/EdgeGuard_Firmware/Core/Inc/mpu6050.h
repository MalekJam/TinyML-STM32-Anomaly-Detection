#ifndef EDGEGUARD_MPU6050_H
#define EDGEGUARD_MPU6050_H
#include <stdint.h>

/* 7-bit I2C addresses: 0x68 (AD0 low), 0x69 (AD0 high). */
#define MPU6050_ADDR 0x68u
#define MPU6050_WHO_AM_I_REG 0x75u
#define MPU6050_ACCEL_LSB_PER_G 16384.0f  /* +-2g */
#define MPU6050_GYRO_LSB_PER_DPS 131.0f  /* +-250 deg/s */

typedef struct {
    int16_t ax, ay, az, gx, gy, gz;
} mpu6050_raw_t;

/* HAL-independent, easily unit-tested I2C bus adapter.
   read/write return 0 on success, nonzero on failure. */
typedef struct {
    void *context;
    int (*read)(void *context, uint8_t address7, uint8_t reg, uint8_t *dst, uint16_t len);
    int (*write)(void *context, uint8_t address7, uint8_t reg, const uint8_t *src, uint16_t len);
    void (*delay_ms)(uint32_t ms);
    uint8_t address7;
} mpu6050_bus_t;

int mpu6050_init(const mpu6050_bus_t *bus, uint8_t *identity);
int mpu6050_read(const mpu6050_bus_t *bus, mpu6050_raw_t *sample);
#endif
