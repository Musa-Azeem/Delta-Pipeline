#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta
import json

event_id_mapping = {
    0: "False Negative Reported",
    1: "Puff Detected",
    2: "Session Detected",
    3: "User Started Smoking Session",
    4: "AI Started Smoking Session",
    5: "User Stopped Smoking Session",
    6: "Timer Stopped Smoking"
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
    starttime_millis = info['App Start Time']
    app_run_time_millis = int(raw['real time'][len(raw)-1] - starttime_millis)
    app_run_time_str = str(timedelta(milliseconds = app_run_time_millis))
    print(f'Total App Run Time: {app_run_time_str}')

    print(events)
    print(raw)
