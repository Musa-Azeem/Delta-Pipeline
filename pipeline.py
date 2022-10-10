import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta


if len(sys.argv) != 2:
    print("Usage: python3 timedeltas.py [path-to-data-directory]")
    exit(1)

os.system('mkdir -p processed')

dir = sys.argv[1]

df = pd.DataFrame()
for file in os.listdir(dir):
    if file.startswith('Session'):
        filename = file.split('.')[1]
        with open(f'{dir}/{file}') as f:
            starttime_millis = int(f.readline().rstrip()[17:])
        session = pd.read_csv(f'{dir}/{file}', skiprows=1)
    else:
        tmp = pd.read_csv(f'{dir}/{file}', skiprows=1)
        df = pd.concat([df, tmp], ignore_index=True)
df = df.sort_values(by=['timestamp'], ignore_index=True)

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

print(df['delta'].describe())
print(df)

df.to_csv(f'processed/{filename}-processed.csv')

# fig = px.line(df.iloc[:len(df)], x='timestamp', y='delta', title='Time delta', 
#                 labels={'timestamp': 'Time', 
#                         'delta': 'Time delta (s)'})
# fig.show(renderer='browser')

fig = px.line(df, x='timestamp', y=['acc_x', 'acc_y', 'acc_z', 'label'], 
            #   color='activity',
              title='Accelerometer Data',
              labels={'timestamp': 'Time', 'variable': 'Legend'})
fig.update_layout(yaxis_title="Acceleration (m/s^2)")
fig.show(renderer='browser')
