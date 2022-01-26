import pandas as pd
import plotly.express as px
from glob import glob
import os
from typing import List
import json
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def load_usage(exp_dir: str, n_peers: int) -> pd.DataFrame:
    data = pd.read_csv(
        os.path.join(exp_dir, '%d/usage.txt' % n_peers),
        sep='\\s+',
        skiprows=1,
        names=['t', 'CPU', 'MEM', 'VMEM']
    )
    data['n_peers'] = n_peers
    data['MA_CPU'] = data['CPU'].rolling(30).mean()
    return data


def load_delivery_ratio(exp_dir: str, n_peers_list: List[int]) -> pd.DataFrame:
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


def main():
    if len(sys.argv) != 2:
        print('Usage: python plot.py EXP_RESULT_DIR')
        exit(0)
    exp_dir = sys.argv[1]
    n_peers_list = sorted(map(
        lambda fp: int(fp.split('/')[-1]),
        glob(os.path.join(exp_dir, '*'))
    ))
    usages = pd.concat([
        load_usage(exp_dir, n_peers)
        for n_peers in n_peers_list
    ])
    usages['MEM'] /= 1e3
    print(usages)

    delivery_ratios = load_delivery_ratio(exp_dir, n_peers_list)

    #  fig = px.line(
    #      delivery_ratios,
    #      x='n_peers',
    #      y='delivery_ratio',
    #      title='Receive Rate',
    #      labels={
    #          'n_peers': '# Peers',
    #          'delivery_ratio': 'Ratio (%)'
    #      }
    #  )
    #  fig.update_layout(
    #      xaxis = dict(
    #          tickmode = 'linear',
    #          dtick = 1
    #      )
    #  )
    #  fig.show()

    #  fig = px.line(
    #      usages,
    #      x='t',
    #      y='MA_CPU',
    #      color='n_peers',
    #      title='CPU Usage',
    #      labels={
    #          't': 'Time (sec)',
    #          'MA_CPU': 'Usage (%)',
    #          'n_peers': '# Peers'
    #      }
    #  )
    #  fig.show()

    #  fig = px.line(
    #      usages,
    #      x='t',
    #      y='MEM',
    #      color='n_peers',
    #      title='Memory Usage',
    #      labels={
    #          't': 'Time (sec)',
    #          'MEM': 'Usage (GB)',
    #          'n_peers': '# Peers'
    #      }
    #  )
    #  fig.show()

    for n_peers in n_peers_list:
        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_trace(go.Scatter(
            x=usages[usages['n_peers'] == n_peers]['t'],
            y=usages[usages['n_peers'] == n_peers]['MA_CPU'],
            marker=dict(color="blue"),
            name='CPU',
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=usages[usages['n_peers'] == n_peers]['t'],
            y=usages[usages['n_peers'] == n_peers]['MEM'],
            marker=dict(color="red"),
            name='Memory'
        ), secondary_y=True)

        fig.update_layout(title_text='CPU & Memory Usage, # Peers: %d' % n_peers)
        fig.update_xaxes(title_text='Time (sec)')
        fig.update_yaxes(title_text='CPU (%)', secondary_y=False)
        fig.update_yaxes(title_text='Memory (GB)', secondary_y=True)
        fig.show()


if __name__ == '__main__':
    main()
