import os

import numpy as np

PROJECT_BASE_DIR = os.getcwd()
SUMMARY_DIR = os.path.join(PROJECT_BASE_DIR, "results")


def parse(filename):
    rewards = []

    with open(filename, "rb") as f:
        for line in f.readlines():
            args = line.split(b"\t")
            rewards.append(float(args[-1]))

    return rewards


def parse_logs(logs_path):
    total_rewards = []
    for f in os.listdir(logs_path):
        f_full_path = os.path.join(logs_path, f)
        total_rewards += parse(f_full_path)

    total_rewards = np.array(total_rewards)
    print("total_reward:", total_rewards.mean())


def main():
    parse_logs(SUMMARY_DIR)


if __name__ == "__main__":
    main()
