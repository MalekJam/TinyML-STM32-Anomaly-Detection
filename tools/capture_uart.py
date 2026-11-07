#!/usr/bin/env python3
"""Save raw MPU6050 readings to CSV; excludes startup/score/status lines."""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from edgeguard.protocol import parse_line


def capture(ser, destination, duration, max_samples=None):
    output=Path(destination); output.parent.mkdir(parents=True,exist_ok=True)
    count=0; dropped=0; begin=time.monotonic(); last=begin
    with output.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow(('t_ms','ax','ay','az','gx','gy','gz'))
        while time.monotonic()-begin<duration and (max_samples is None or count<max_samples):
            data=ser.readline()
            if not data: continue
            parsed=parse_line(data.decode('ascii',errors='replace'))
            if not parsed: dropped += 1; continue
            if parsed['kind']=='sample':
                writer.writerow([parsed[k] for k in ('t_ms','ax','ay','az','gx','gy','gz')]); count+=1
            elif parsed['kind']=='result':
                status='ANOMALY' if parsed['anomaly'] else 'NORMAL'
                print(f"{parsed['mode']:9s}: {status:7s} score={parsed['score']:.6f} threshold={parsed['threshold']:.6f}")
            elif parsed['kind']=='status': print(parsed['message'])
            if time.monotonic()-last>5:
                f.flush(); print(f"Recorded {count} samples to {output}");last=time.monotonic()
    print(f"Done: {count} samples ({dropped} malformed/ignored messages) -> {output}")
    if count < 32:
        raise RuntimeError("Insufficient readings. Check FTDI RX pin, common GND, and COM port.")
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True,help='COM5 or /dev/ttyUSB0')
    p.add_argument('--baud',type=int,default=115200)
    p.add_argument('--seconds',type=int,default=120)
    p.add_argument('--output',default='data/normal.csv')
    a=p.parse_args()
    try: import serial
    except ImportError as exc: raise SystemExit('Install dependencies: pip install -r requirements.txt') from exc
    try:
        with serial.Serial(a.port,a.baud,timeout=0.5) as s:
            capture(s,a.output,a.seconds)
    except serial.SerialException as exc:
        raise SystemExit(f"Serial connection failed: {exc}") from exc
