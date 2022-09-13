import os
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta


data_dir = f'data/new_tests'
project = '2022-09-12_15_30_51-modified'
dir = f'{data_dir}/{project}'

df = pd.DataFrame()
for file in os.listdir(dir):
    if file.startswith('Session'):
        with open(f'{dir}/{file}') as f:
            starttime_millis = int(f.readline().rstrip()[17:])
        session = pd.read_csv(f'{dir}/{file}', skiprows=1)
    else:
        tmp = pd.read_csv(f'{dir}/{file}', skiprows=1)
        df = pd.concat([df, tmp], ignore_index=True)
df = df.sort_values(by=['timestamp'], ignore_index=True)

df = df.loc[:len(df)/2, :]


print(len(df))
# get readable time (delta from start time)
real_times = []
for time_millis in df['real time']:
    delta = (time_millis - starttime_millis) # convert to seconds
    real_times.append(str(timedelta(milliseconds=delta)))
df['human time'] = real_times


# get time delta at each sample
deltas = []
for i, timestamp in enumerate(df['timestamp']):
    if i == 0:
        deltas.append(np.nan)
        continue
    # get time since last sample, convert to Hz
    deltas.append( (df['timestamp'][i] - df['timestamp'][i-1]) / 1e9)
df['delta'] = deltas

df.to_csv(f'{data_dir}/processed/{project}-processed.csv')

print(df['delta'].describe())
print(df)

fig = px.line(df, x='human time', y='delta', title='Time delta', 
                labels={'human time': 'Time', 
                        'delta': 'Time delta (s)'})
fig.show(renderer='browser')
