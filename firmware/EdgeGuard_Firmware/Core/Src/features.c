#include "motion_features.h"
#include <math.h>
#include <string.h>
void feature_window_reset(feature_window_t *w) { memset(w, 0, sizeof(*w)); }
void feature_window_push(feature_window_t *w, const mpu6050_raw_t *s) {
    if (w->count >= EDGEGUARD_WINDOW) return;
    const float v[6] = {
        (float)s->ax / MPU6050_ACCEL_LSB_PER_G,
        (float)s->ay / MPU6050_ACCEL_LSB_PER_G,
        (float)s->az / MPU6050_ACCEL_LSB_PER_G,
        (float)s->gx / MPU6050_GYRO_LSB_PER_DPS,
        (float)s->gy / MPU6050_GYRO_LSB_PER_DPS,
        (float)s->gz / MPU6050_GYRO_LSB_PER_DPS
    };
    for (unsigned i = 0; i < 6; ++i) {
        w->sums[i] += v[i];
        w->squares[i] += v[i] * v[i];
    }
    ++w->count;
}
int feature_window_finish(feature_window_t *w, float features[EDGEGUARD_FEATURES]) {
    if (w->count != EDGEGUARD_WINDOW) return 0;
    for (unsigned i = 0; i < 6; ++i) {
        float mean = w->sums[i] / (float)EDGEGUARD_WINDOW;
        float variance = w->squares[i] / (float)EDGEGUARD_WINDOW - mean * mean;
        features[i] = mean;
        features[i + 6u] = sqrtf(fmaxf(variance, 0.0f));
    }
    feature_window_reset(w);
    return 1;
}
