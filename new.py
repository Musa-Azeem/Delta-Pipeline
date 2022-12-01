from pandas import read_csv
dir = '2022-09-03_18_30_24'
df = read_csv(f'{dir}/raw/{dir}.0.csv',skiprows=1)
df = df.sort_values(by='event_timestamp')
df['event_timestamp'] = (df['event_timestamp']-df['event_timestamp'][0])/1000000000
df['event_timestamp_dt'] = df['event_timestamp'].diff()

import plotly.express as px
fig = px.line(data_frame=df,y=['event_timestamp_dt'], labels=['x','y'])
fig.update_layout(
    xaxis_title="index", yaxis_title="timestamp"
)
fig.show(renderer='browser')

print(len(df))