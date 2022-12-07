#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from datetime import timedelta
import json

event_id_mapping = {
    "False Negative Reported": 0,
    "Puff Detected": 1,
    "Session Detected": 2,
    "User Started Smoking Session": 3,
    "AI Started Smoking Session": 4,
    "User Stopped Smoking Session": 5,
    "Timer Stopped Smoking": 6
}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 timedeltas.py [path-to-data-directory]")
        exit(1)

    os.system('mkdir -p processed')

    dir = sys.argv[1]

    events = pd.DataFrame()
    info = {}
    raw = pd.DataFrame()

    for file in os.listdir(dir):
        if file == 'events.csv':
            events = pd.read_csv(f'{dir}/{file}')
        elif file == 'Info.json':
            info = json.load(open(f'{dir}/{file}', 'r'))

    # Read Raw Files
    for file in os.listdir(f'{dir}/raw'):
        tmp = pd.read_csv(f'{dir}/raw/{file}', skiprows=1)
        raw = pd.concat([raw, tmp], ignore_index=True)
    raw = raw.sort_values(by=['timestamp'], ignore_index=True)

    # get app run length (delta from start time)
    app_run_time_millis = int(raw['real time'].iloc[-1] - info['App Start Time'])
    app_run_time_str = str(timedelta(milliseconds = app_run_time_millis))
    print(f'Total App Run Time: {app_run_time_str}')

    # add readable times to raw df
    readable_times = []
    for time_millis in raw['real time']:
        delta = (time_millis - info['App Start Time'])
        readable_times.append(str(timedelta(milliseconds=delta)))
    raw['readable time'] = readable_times

    # We sample at 20 Hz, so average dt is 0.05 s
    # avg_dt = (raw['timestamp'].iloc[-1] - raw['timestamp'].iloc[0]) / len(raw['timestamp']) / 1e9

    # Get each smoking session
    smoking_sessions = pd.DataFrame(columns=['starttime', 'stoptime'])   # start and stop of all sessions

    # Get false negatives (missed smoking sessions)

    app_start_datetime = datetime.strptime(info['App Start Time Readable'], "%Y-%m-%d_%H_%M_%S")
    false_negatives = events[events['event_id'] == event_id_mapping["False Negative Reported"]]

    for false_negative_time in false_negatives['time reported']:
        time_reported_datetime = datetime.strptime(false_negative_time, '%Y-%m-%d_%H_%M_%S')
        # Get time in milliseconds of this event since app start time
        time_reported_millis = int((time_reported_datetime - app_start_datetime).total_seconds()*1e3 + info['App Start Time'])
        stoptime = int(time_reported_millis + 8 * 60 * 1e3)  # We don't know how long the smoking session was - assume 8 minutes
        smoking_sessions = pd.concat([smoking_sessions, pd.DataFrame({'starttime': [time_reported_millis], 'stoptime': [stoptime]})], ignore_index=True)

    # Get detected / reported smoking sessions

    # Get the start and stop time of each session in milliseconds since app start time
    # anytime the 'real time' in raw is in this range (greater than stop and less than start), make 'in session' of that row = 1

    # Add smoking status to raw
    raw['is smoking'] = 0
    for i in range(len(smoking_sessions)):
        raw.loc[(raw['real time'] >= smoking_sessions['starttime'][i]) & (raw['real time'] <= smoking_sessions['stoptime'][i]), 'is smoking'] = 1
        print(raw)
    # get time delta at each sample
    # df = raw
    # deltas = []
    # for i, timestamp in enumerate(df['timestamp']):
    #     if i == 0:
    #         deltas.append(np.nan)
    #         continue
    #     # get time since last sample, convert to Hz
    #     deltas.append( (df['timestamp'][i] - df['timestamp'][i-1]) / 1e9)
    # df['delta'] = deltas

    fig = px.line(raw, y=['is smoking', 'acc_x', 'acc_y', 'acc_z'], title='Time delta', 
                    labels={'timestamp': 'Time', 
                            'delta': 'Time delta (s)'})
    fig.show(renderer='browser')



    # print(events)
    # print(raw)
