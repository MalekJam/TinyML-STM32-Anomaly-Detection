#ifndef EDGEGUARD_INFERENCE_H
#define EDGEGUARD_INFERENCE_H
#include "motion_features.h"
/* model type: 0 = heuristic fallback, 1 = autoencoder TinyML */
int edgeguard_model_ready(void);
float edgeguard_threshold(void);
float edgeguard_score(const float feature[EDGEGUARD_FEATURES]);
int edgeguard_anomaly(float score);
#endif
