#include "inference.h"
#include "model_generated.h"
#include <math.h>

int edgeguard_model_ready(void) { return EDGEGUARD_MODEL_READY; }
float edgeguard_threshold(void) {
#if EDGEGUARD_MODEL_READY
    return edgeguard_threshold_value;
#else
    return 1.0f;
#endif
}
float edgeguard_score(const float f[EDGEGUARD_FEATURES]) {
#if EDGEGUARD_MODEL_READY
    float z[EDGEGUARD_FEATURES], hidden[EDGEGUARD_HIDDEN];
    float error = 0.0f;
    for (unsigned i=0; i<EDGEGUARD_FEATURES; ++i) {
        z[i] = (f[i] - edgeguard_normal_mean[i]) / edgeguard_normal_scale[i];
    }
    for (unsigned h=0; h<EDGEGUARD_HIDDEN; ++h) {
        float s = edgeguard_b1[h];
        for (unsigned i=0; i<EDGEGUARD_FEATURES; ++i)
            s += z[i] * edgeguard_w1[i][h];
        hidden[h] = tanhf(s);
    }
    for (unsigned i=0; i<EDGEGUARD_FEATURES; ++i) {
        float reconstructed = edgeguard_b2[i];
        for (unsigned h=0; h<EDGEGUARD_HIDDEN; ++h)
            reconstructed += hidden[h] * edgeguard_w2[h][i];
        float d = reconstructed - z[i];
        error += d * d;
    }
    return error / (float)EDGEGUARD_FEATURES;
#else
    /* Relative magnitude of acceleration mean and gyroscope motion.
       Used only BEFORE real model training; NOT ML. */
    float acc = sqrtf(f[0]*f[0] + f[1]*f[1] + f[2]*f[2]);
    float gyro = sqrtf(f[3]*f[3] + f[4]*f[4] + f[5]*f[5]);
    float gyro_var = sqrtf(f[9]*f[9] + f[10]*f[10] + f[11]*f[11]);
    float score_a = fabsf(acc - 1.0f) / 0.25f;
    float score_g = gyro / 45.0f;
    float score_v = gyro_var / 25.0f;
    return fmaxf(score_a, fmaxf(score_g, score_v));
#endif
}
int edgeguard_anomaly(float score) { return score > edgeguard_threshold(); }
