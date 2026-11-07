#!/usr/bin/env python3
"""Interactive PC dashboard for live UART data, not deployed on STM32."""
import argparse
import sys
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from edgeguard.protocol import parse_line


def run(port,baud):
    import serial
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    serial_port=serial.Serial(port,baud,timeout=0)
    xs=deque(maxlen=250); acc=deque(maxlen=250)
    score=deque(maxlen=250); score_x=deque(maxlen=250)
    fig,ax=plt.subplots(figsize=(11,5))
    ax.set_xlabel('Time (s)');ax.set_ylabel('Acceleration magnitude (g)')
    ax.set_title('EdgeGuard AI — Live MPU6050')
    l1,=ax.plot([],[],label='Acceleration |a|')
    (status_text,)=[ax.text(0.02,0.92,'Waiting for data...',transform=ax.transAxes)]
    ax.legend(loc='upper right')
    def update(_):
        for __ in range(200):
            data=serial_port.readline()
            if not data: break
            row=parse_line(data.decode('ascii',errors='replace'))
            if not row: continue
            if row['kind']=='sample':
                x=row['t_ms']/1000
                a=((row['ax']/16384)**2+(row['ay']/16384)**2+(row['az']/16384)**2)**0.5
                xs.append(x);acc.append(a)
            if row['kind']=='result':
                status='ANOMALY' if row['anomaly'] else 'NORMAL'
                status_text.set_text(f"{row['mode']} | {status} | score {row['score']:.4f} / {row['threshold']:.4f}")
        if xs:
            l1.set_data(list(xs),list(acc))
            ax.set_xlim(max(0,xs[-1]-10),max(10,xs[-1]+0.1))
            ax.set_ylim(0,max(2.0, max(acc)*1.15))
        return l1,status_text
    anim=FuncAnimation(fig,update,interval=70,blit=False,cache_frame_data=False)
    try: plt.show()
    finally: serial_port.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--baud',type=int,default=115200)
    a=p.parse_args();run(a.port,a.baud)
