#!/usr/bin/env python3

from glob import glob
from pathlib import Path
from tap import Tap
from typing import List
from typing import Optional
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_usage(exp_dir: Path, n_peers: int) -> pd.DataFrame:
    data = pd.read_csv(
        os.path.join(exp_dir, '%d/usage.txt' % n_peers),
        sep='\\s+',
        skiprows=1,
        names=['t', 'CPU', 'MEM', 'VMEM']
    )
    data['n_peers'] = n_peers
    data['MA_CPU'] = data['CPU'].rolling(30).mean()
    return data


def load_delivery_ratio(exp_dir: Path, n_peers_list: List[int]) -> pd.DataFrame:
    rates = list()
    for n_peers in n_peers_list:
        file_path = os.path.join(exp_dir, '%d/result.json' % n_peers)
        if os.path.exists(file_path):
            with open(file_path) as f:
                rates.append(float(json.load(f)['delivery_ratio']) * 100.)
        else:
            rates.append(0.)

    return pd.DataFrame({
        'n_peers': n_peers_list,
        'delivery_ratio': rates
    })


class MyArgParser(Tap):
    # the directory containing the experiemental results
    exp_dir: Path = Path('./results')
    # specify max number of threads used in this experiment
    num_thread: int = 32
    # specify max memory size (GB) used in this experiment
    memory_size: int = 16
    # if not specified, plot the curves interactively on the browser
    output_dir: Optional[Path] = None


args = MyArgParser().parse_args()

# load data
n_peers_list = sorted(map(
    lambda fp: int(fp.split('/')[-1]),
    glob(os.path.join(args.exp_dir, '*'))
))
usages = pd.concat([
    load_usage(args.exp_dir, n_peers)
    for n_peers in n_peers_list
])
usages['MEM'] /= 1e3


# plot delivery ratio
delivery_ratios = load_delivery_ratio(args.exp_dir, n_peers_list)
fig = px.line(
    delivery_ratios,
    x='n_peers',
    y='delivery_ratio',
    title='Receive Rate',
    labels={
        'n_peers': '# Peers',
        'delivery_ratio': 'Ratio (%)'
    }
)
fig.update_layout(
    xaxis = dict(
        tickmode = 'linear',
        dtick = 1
    )
)
if args.output_dir:
    os.makedirs(args.output_dir, exist_ok=True)
    fig.write_image(os.path.join(
        args.output_dir,
        'delivery-ratio.jpg'
    ))
else:
    fig.show()


# plot each CPU & memory usage
for n_peers in n_peers_list:
    trace1 = go.Scatter(
        x=usages[usages['n_peers'] == n_peers]['t'],
        y=usages[usages['n_peers'] == n_peers]['MA_CPU'],
        marker=dict(color="blue"),
        name='CPU',
        yaxis='y1',
    )
    trace2 = go.Scatter(
        x=usages[usages['n_peers'] == n_peers]['t'],
        y=usages[usages['n_peers'] == n_peers]['MEM'],
        marker=dict(color="red"),
        name='Memory',
        yaxis='y2',
    )
    layout = go.Layout(
        title='CPU & Memory Usage, # Peers: %d' % n_peers,
        xaxis={
            'title': 'Time (sec)',
            'range': [0, 20],
            'dtick': 1,
        },
        yaxis={
            'title': 'CPU (%)',
            'range': [0, 100 * args.num_thread],
            'dtick': 400,
        },
        yaxis2={
            'title': 'Memory (GB)',
            'overlaying': 'y',
            'side': 'right',
            'range': [0, 16],
            'dtick': 1,
        },
        legend={
            'y': 1.18,
            'x': 0.92
        }
    )
    fig = go.Figure(
        data=[trace1, trace2],
        layout=layout
    )
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        fig.write_image(os.path.join(
            args.output_dir,
            'n-peers-%02d.jpg' % n_peers
        ))
    else:
        fig.show()
