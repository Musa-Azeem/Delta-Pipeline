# Delta-Pipeline
Pipeline to process and visualize data from the Delta android wear app

## Usage

To graph accelerometer data: 
```
python3 pipeline.py [path-to-data-directory]
```

To visualize time deltas between samples: 
```
python3 timedeltas.py [path-to-data-directory]
```

For example: `python3 pipeline.py raw_data/2022-09-12_15_30_51/`