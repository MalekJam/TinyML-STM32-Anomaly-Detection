#!/usr/bin/env python3
"""Summarize recorded real UART CSV; optional JSON export for evidence."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from edgeguard.features import read_capture


def analyze(path):
    samples=read_capture(path)
    with Path(path).open(newline='',encoding='utf-8') as file:
        rows=list(csv.DictReader(file))
    times=np.asarray([int(row['t_ms']) for row in rows],dtype=np.int64)
    duration=(times[-1]-times[0])/1000.0 if len(times)>1 else 0
    diffs=np.diff(times)
    a=samples[:,:3].astype(np.float64)/16384.
    mag=np.linalg.norm(a,axis=1)
    return {
        'file':str(path),'sample_count':int(len(samples)),
        'duration_seconds':round(float(duration),3),
        'observed_sample_rate_hz':round(float((len(samples)-1)/duration),2) if duration>0 else None,
        'mean_sample_interval_ms':round(float(np.mean(diffs)),3) if len(diffs) else None,
        'largest_sample_gap_ms':int(np.max(diffs)) if len(diffs) else None,
        'accel_magnitude_mean_g':round(float(np.mean(mag)),4),
        'accel_magnitude_min_g':round(float(np.min(mag)),4),
        'accel_magnitude_max_g':round(float(np.max(mag)),4),
        'accel_raw_saturated_samples':int(np.count_nonzero(np.any(np.abs(samples[:,:3].astype(np.int32))>=32767,axis=1))),
        'gyro_raw_saturated_samples':int(np.count_nonzero(np.any(np.abs(samples[:,3:].astype(np.int32))>=32767,axis=1)))
    }

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True);p.add_argument('--output')
    a=p.parse_args()
    result=analyze(a.input)
    rendered=json.dumps(result,indent=2)
    print(rendered)
    if a.output:
        Path(a.output).write_text(rendered+'\n',encoding='utf-8')
