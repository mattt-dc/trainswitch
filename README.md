# TrainSwitch

## Overview
TrainSwitch is a proof of concept of switching between videos streams when a train is detected.

## Getting Started

If not using existing streams then these can be started by running MonaServer and opening a separate OBS instance for each stream. The input stream paths are set in stream_manager.py.

Tested with python 3.8.

The data/weights folder should include yolox_m.path from [the yolox repository](https://github.com/Megvii-BaseDetection/YOLOX). The matching config (yolox_m.py) should be copied to the configs folder (from exps/default).

1. If using pip, install dependencies by running: ```pip install -r requirements.txt```
2. Then run with:
```python main.py```
