#!/usr/bin/env python3
"""Train on actual normal CSV samples; optional anomaly CSV is EVALUATION ONLY.
Normal-only train/validation split is chronological to reduce time leakage.
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from edgeguard.features import read_capture, extract_features
from edgeguard.model import fit, scores, make_header


def train(normal, anomaly=None, header=ROOT/'firmware/EdgeGuard_Firmware/Core/Inc/model_generated.h', report=None, epochs=240):
    x = extract_features(read_capture(normal))
    if len(x) < 40:
        raise ValueError(f"Need 40 or more normal windows (~12.8s). Got {len(x)}")
    split = max(24, int(len(x)*0.75))
    if len(x) - split < 6:
        raise ValueError("Insufficient validation windows")
    model = fit(x[:split], epochs=epochs)
    train_err = scores(model, x[:split]); valid_err = scores(model, x[split:])
    threshold = float(max(np.quantile(valid_err, 0.99), np.quantile(train_err, 0.99)) * 1.25 + 1e-8)
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("Invalid fitted threshold")
    output = Path(header)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(make_header(model,threshold),encoding='utf-8')
    result = {"model": "12-8-12_tanh_autoencoder", "window_samples":32,
              "sampling_target_hz":100, "normal_train_windows":int(split),
              "normal_val_windows":int(len(x)-split),
              "threshold_mse":threshold,
              "normal_validation_false_positive_rate":float(np.mean(valid_err>threshold)),
              "training_data":str(normal),"anomaly_test_data":str(anomaly) if anomaly else None,
              "hardware_tested":False,
              "method": "chronological split 75% training / 25% validation, normal-only learning"}
    if anomaly:
        anomaly_x = extract_features(read_capture(anomaly))
        result["anomaly_test_windows"] = int(len(anomaly_x))
        result["anomaly_test_detection_rate"] = float(np.mean(scores(model,anomaly_x)>threshold))
    if report:
        p=Path(report);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result,indent=2)+"\n",encoding='utf-8')
    print(json.dumps(result,indent=2))
    print(f"\nGenerated firmware header: {output}")
    return model,result

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--normal',required=True,help='Actual stationary-normal raw CSV')
    p.add_argument('--anomaly',help='Separate anomalous data; for testing only')
    p.add_argument('--header',default=str(ROOT/'firmware/EdgeGuard_Firmware/Core/Inc/model_generated.h'))
    p.add_argument('--report',default=str(ROOT/'docs/assets/training-results.json'))
    p.add_argument('--epochs',type=int,default=240)
    a=p.parse_args()
    train(a.normal,a.anomaly,a.header,a.report,a.epochs)
