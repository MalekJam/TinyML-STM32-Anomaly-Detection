#!/usr/bin/env python3
"""Generate SYNTHETIC MPU6050 raw data for host tests, never as field evidence."""
import argparse
import csv
from pathlib import Path
import numpy as np


def make_dataset(path, count=8000, anomaly=False, seed=41):
    rng=np.random.default_rng(seed)
    i=np.arange(count)
    a=np.column_stack((
        0.06+0.003*np.sin(i*0.013),
        -0.03+0.005*np.cos(i*0.017),
        0.997+0.003*np.sin(i*0.021)))
    a += rng.normal(0,0.009,(count,3))
    g=rng.normal(0,0.7,(count,3)) + np.array([0.4,-0.2,0.1])
    if anomaly:
        # Each window has significant shaking / rotation, meant to be clearly abnormal.
        a[:,0] += 0.3*np.sin(i*0.30)
        a[:,1] += 0.5*np.sin(i*0.27)
        g[:,0] += 65*np.sin(i*0.22)
        g[:,1] += 50*np.cos(i*0.28)
    raw=np.column_stack((a*16384,g*131))
    raw=np.clip(np.rint(raw),-32768,32767).astype(np.int16)
    dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(('t_ms','ax','ay','az','gx','gy','gz'))
        for t,values in enumerate(raw): writer.writerow((t*10,*[int(v) for v in values]))
    print(f"SYNTHETIC: {dest} ({count} rows)")
    return raw

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',default='data')
    p.add_argument('--normal-samples',type=int,default=8000)
    p.add_argument('--anomaly-samples',type=int,default=3200)
    args=p.parse_args()
    base=Path(args.output_dir)
    make_dataset(base/'synthetic_normal.csv',args.normal_samples,False)
    make_dataset(base/'synthetic_anomaly.csv',args.anomaly_samples,True,44)
