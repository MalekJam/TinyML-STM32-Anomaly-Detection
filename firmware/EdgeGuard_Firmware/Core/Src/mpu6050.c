#include "mpu6050.h"

static int write_u8(const mpu6050_bus_t *b, uint8_t reg, uint8_t value) {
    return b->write(b->context, b->address7, reg, &value, 1u);
}
static int16_t be16(const uint8_t *p) {
    return (int16_t)((uint16_t)((uint16_t)p[0] << 8) | p[1]);
}

int mpu6050_init(const mpu6050_bus_t *bus, uint8_t *identity) {
    uint8_t who = 0;
    if (!bus || !bus->read || !bus->write || !bus->delay_ms) return -1;
    if (bus->read(bus->context, bus->address7, MPU6050_WHO_AM_I_REG, &who, 1u)) return -2;
    if (identity) *identity = who;
    if (who != 0x68u) return -3;
    if (write_u8(bus, 0x6Bu, 0x80u)) return -4; /* Reset */
    bus->delay_ms(100);
    if (write_u8(bus, 0x6Bu, 0x01u)) return -5; /* X gyro reference, wake */
    if (write_u8(bus, 0x1Au, 0x03u)) return -6; /* DLPF enabled */
    if (write_u8(bus, 0x19u, 0x09u)) return -7; /* 1kHz / (9+1) = 100Hz */
    if (write_u8(bus, 0x1Bu, 0x00u)) return -8; /* Gyro +-250 deg/s */
    if (write_u8(bus, 0x1Cu, 0x00u)) return -9; /* Accel +-2g */
    bus->delay_ms(20);
    return 0;
}

int mpu6050_read(const mpu6050_bus_t *bus, mpu6050_raw_t *s) {
    uint8_t r[14];
    if (!bus || !s || !bus->read) return -1;
    if (bus->read(bus->context, bus->address7, 0x3Bu, r, sizeof r)) return -2;
    s->ax = be16(&r[0]);  s->ay = be16(&r[2]);  s->az = be16(&r[4]);
    /* r[6..7] is the temperature measurement; intentionally skipped */
    s->gx = be16(&r[8]);  s->gy = be16(&r[10]); s->gz = be16(&r[12]);
    return 0;
}
