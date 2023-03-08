## Installation
1. install python2
2. run `./setup.sh`

## Train new model - multi video variation
1. `cd multi_video_sim_training`
2. `python generate_video.py`
3. Place traces in `cooked_test_traces` and `cooked_traces` (using a script from the repo 'traces' that converts to pensieve format)
4. run `python multi_agent_entropy.py` (decresing entropy version like the paper), or const entropy with `python multi_agent.py`
5. Monitor training: `python -m tensorflow.tensorboard --logdir=./multi_video_sim_training/results/` (view in `localhost:6006`)

## Test models
Selenium on top of a PyVirtualDisplay is used and the actual graphics is disabled.
1. Place trained RL model in `rlserver/results`
2. `cd run_exp`
3. (Edit `TRACE_PATH` in the script `run_exp/run_all_traces`)
4. `python run_all_traces.py`
5. Generate plot `python plot_results.py`

TODO: maybe divide by 2 the video size since each chunk is 2 seconds long (and not 4).