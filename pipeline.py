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
    if len(sys.argv) != 3:
        print("Usage: python3 timedeltas.py [path-to-data-directory] [timedeltas | data]")
        exit(1)

    dir = sys.argv[1]
    timedelta_mode = sys.argv[2] == 'timedeltas'

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

    # Get each smoking session
    smoking_sessions = pd.DataFrame(columns=['starttime', 'stoptime'])   # start and stop of all sessions

    start_times = events[(events['event_id'] == event_id_mapping['User Started Smoking Session']) | \
                         (events['event_id'] == event_id_mapping['AI Started Smoking Session'])]['time'].reset_index(drop=True)
                    
    stop_times = events[(events['event_id'] == event_id_mapping['User Stopped Smoking Session']) | \
                        (events['event_id'] == event_id_mapping['Timer Stopped Smoking'])]['time'].reset_index(drop=True)

    smoking_sessions['starttime'] = start_times
    smoking_sessions['stoptime'] = stop_times

    # If a start session did not have an end session associated with it, set the end after 8 minutes
    compute_replacement_value = lambda row: int(row['starttime'] + 8*60*1e3)
    smoking_sessions['stoptime'].fillna(smoking_sessions.apply(compute_replacement_value, axis=1), inplace=True)


    # Get false negatives (missed smoking sessions)
    app_start_datetime = datetime.strptime(info['App Start Time Readable'], "%Y-%m-%d_%H_%M_%S")
    false_negatives = events[events['event_id'] == event_id_mapping["False Negative Reported"]]

    for false_negative_time in false_negatives['time reported']:
        time_reported_datetime = datetime.strptime(false_negative_time, '%Y-%m-%d_%H_%M_%S')
        # Get time in milliseconds of this event since app start time
        time_reported_millis = int((time_reported_datetime - app_start_datetime).total_seconds()*1e3 + info['App Start Time'])
        stoptime = int(time_reported_millis + 8 * 60 * 1e3)  # We don't know how long the smoking session was - assume 8 minutes
        smoking_sessions = pd.concat([smoking_sessions, pd.DataFrame({'starttime': [time_reported_millis], 'stoptime': [stoptime]})], ignore_index=True)
    

    # Get the start and stop time of each session in milliseconds since app start time
    # anytime the 'real time' in raw is in this range (greater than stop and less than start), make 'in session' of that row = 1

    # Add smoking status to raw
    raw['is smoking'] = 10      # Default value (not smoking) is 10
    for i in range(len(smoking_sessions)):
        # set value to 15 (smoking) if within the range of a smoking session
        raw.loc[(raw['real time'] >= smoking_sessions['starttime'][i]) & (raw['real time'] <= smoking_sessions['stoptime'][i]), 'is smoking'] = 15

    fig = px.line(raw, x='readable time', y=['is smoking', 'acc_x', 'acc_y', 'acc_z'], title='Accelerometer data', 
                    labels={'readable time': 'Time Since start'}) 
    # fig.show(renderer='browser')

    if timedelta_mode:
        # Calculate and display timedeltas
        # get time delta at each sample
        deltas = []
        for i, timestamp in enumerate(raw['timestamp']):
            if i == 0:
                deltas.append(np.nan)
                continue
            # get time since last sample, convert to Hz
            deltas.append( (raw['timestamp'][i] - raw['timestamp'][i-1]) / 1e9)
        raw['delta'] = deltas

        fig = px.line(raw, y='delta', title='Time delta', 
                labels={'delta': 'Time delta (s)'})
    
    fig.show(renderer='browser')