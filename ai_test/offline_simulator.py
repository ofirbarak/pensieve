import os
import shutil
import numpy as np
from env import BUFFER_THRESH, MILLISECONDS_IN_SECOND, VIDEO_CHUNCK_LEN, Environment
from agents.bba_agent import ABRAgent as BBA_Agent


A_DIM = 10
VIDEO_BIT_RATE = [200, 300, 450, 750, 1200, 1850, 2850, 4300, 6000, 8000]  # Kbps
M_IN_K = 1000.0
M_IN_B = 1000000.0
REBUF_PENALTY = 4.3  # 1 sec rebuffering -> 3 Mbps
SMOOTH_PENALTY = 1
RANDOM_SEED = 42
RAND_RANGE = 1000
DEFAULT_QUALITY = 3  # default video quality without agent

PROJECT_BASE_DIR = os.getcwd()
SUMMARY_DIR = os.path.join(PROJECT_BASE_DIR, "results")
TRAIN_TRACES = os.path.join(PROJECT_BASE_DIR, "cooked_traces/train")


def get_reward(bitrate, last_bitrate, rebuf):
    return (
        bitrate / M_IN_K
        - REBUF_PENALTY * rebuf
        - SMOOTH_PENALTY * np.abs(bitrate - last_bitrate) / M_IN_K
    )


def simulate(log_path: str, trace_file: str):
    net_env = Environment(fixed_env=True, trace_file=trace_file)

    mask = net_env.video_masks[net_env.video_idx]
    available_bitrates = np.array(VIDEO_BIT_RATE) * np.array(mask)
    available_bitrates = available_bitrates[available_bitrates != 0]
    agent = BBA_Agent(
        video_sizes=net_env.video_sizes[net_env.video_idx],
        buffer_size_in_ms=BUFFER_THRESH,
        chunk_len_in_ms=VIDEO_CHUNCK_LEN,
        bitrates_in_kbps=available_bitrates.tolist(),
        # lookahead=1
    )

    bitrate = DEFAULT_QUALITY
    last_birate = bitrate

    time_stamp = 0
    round = 0
    end_of_video = False
    buffer_size = 2

    state = {
        "curr_buffer_size_in_ms": 0,
        "last_chunk_sending_time": 0,
        "next_chunk_sizes_in_bytes": net_env.video_sizes[net_env.video_idx][0],
        "rebuf_in_ms": 0,
    }

    while not end_of_video:
        bitrate = agent.get_bitrate_index(**state)

        assert bitrate % 1 == 0
        bitrate = int(bitrate)

        last_buffer_size = buffer_size

        (
            delay,
            sleep_time,
            buffer_size,
            rebuf,
            chunk_size,
            end_of_video,
            video_chunk_remain,
            video_num_chunks,
            next_video_chunk_sizes,
            mask,
        ) = net_env.get_video_chunk(bitrate)

        reward = get_reward(
            available_bitrates[bitrate], available_bitrates[last_birate], rebuf
        )

        state["curr_buffer_size_in_ms"] = buffer_size
        state["rebuf_in_ms"] = rebuf
        state["last_chunk_sending_time"] = buffer_size + delay - last_buffer_size
        state["next_chunk_sizes_in_bytes"] = next_video_chunk_sizes

        agent.update(reward)

        with open(log_path, "ab") as log_file:
            time_stamp += delay  # in ms
            time_stamp += sleep_time  # in ms

            msg = f"{time_stamp}\t{bitrate}\t{buffer_size}\t{rebuf}\t{chunk_size}\t{delay}\t{reward}\n"
            log_file.write(bytes(msg, "utf-8"))
            log_file.flush()

        last_birate = bitrate
        round += 1


def main():
    if os.path.exists(SUMMARY_DIR):
        shutil.rmtree(SUMMARY_DIR)

    os.mkdir(SUMMARY_DIR)

    for f in os.listdir(TRAIN_TRACES):
        log_path = os.path.join(SUMMARY_DIR, f)
        simulate(log_path, os.path.join(TRAIN_TRACES, f))


if __name__ == "__main__":
    main()
