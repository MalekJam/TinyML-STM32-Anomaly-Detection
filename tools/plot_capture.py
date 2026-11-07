#!/usr/bin/env python3
"""Build a GitHub-ready figure from actual CSV captures. --synthetic adds a warning."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from edgeguard.features import read_capture


def plot(normal,anomaly,output,synthetic=False):
    x=read_capture(normal);y=read_capture(anomaly)
    fig,axs=plt.subplots(2,1,figsize=(11.5,6.2),sharey=True)
    for ax,samples,title in zip(axs,[x,y],['Normal motion','Abnormal movement']):
        t=np.arange(len(samples))/100.
        mag=np.linalg.norm(samples[:,:3].astype(np.float64)/16384.0,axis=1)
        ax.plot(t,mag,lw=0.8)
        ax.set_ylabel('Accel. magnitude (g)')
        ax.set_title(title,loc='left',fontsize=11)
        ax.grid(alpha=0.2)
    axs[1].set_xlabel('Time (seconds, assuming 100Hz sampling)')
    fig.suptitle('EdgeGuard AI · MPU6050 capture comparison',fontsize=16,fontweight='bold')
    if synthetic:
        fig.text(0.5,0.5,'SYNTHETIC DEMONSTRATION — NOT REAL HARDWARE DATA',
                 ha='center',va='center',rotation=16,fontsize=16,alpha=0.25,color='red')
    fig.tight_layout(rect=[0,0,1,0.95])
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(dest,dpi=150,bbox_inches='tight')
    plt.close(fig)
    print(dest)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--normal',required=True);p.add_argument('--anomaly',required=True)
    p.add_argument('--output',default='docs/assets/real_capture.png');p.add_argument('--synthetic',action='store_true')
    a=p.parse_args();plot(a.normal,a.anomaly,a.output,a.synthetic)
