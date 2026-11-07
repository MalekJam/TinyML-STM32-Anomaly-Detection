#ifndef EDGEGUARD_FEATURES_H
#define EDGEGUARD_FEATURES_H
#include <stdint.h>
#include "mpu6050.h"
#define EDGEGUARD_WINDOW 32u
#define EDGEGUARD_CHANNELS 6u
#define EDGEGUARD_FEATURES 12u

typedef struct {
    float sums[EDGEGUARD_CHANNELS];
    float squares[EDGEGUARD_CHANNELS];
    uint32_t count;
} feature_window_t;

void feature_window_reset(feature_window_t *w);
void feature_window_push(feature_window_t *w, const mpu6050_raw_t *s);
/* returns 1 if window complete; emits means [0..5] then stddevs [6..11] */
int feature_window_finish(feature_window_t *w, float features[EDGEGUARD_FEATURES]);
#endif
