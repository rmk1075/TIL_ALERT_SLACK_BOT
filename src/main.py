import sys
import datetime
import time
import argparse
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.absolute().parent.absolute()))

from src.core.runner import Runner

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--alert", help="excute alert mode", action="store_true")
parser.add_argument("-c", "--config_path", help="path of config file", type=str, default=str(pathlib.Path(__file__).parent.absolute().parent.absolute()) + "/config/config.json")

if __name__ == "__main__":
    # 현재 시간 log
    print(time.strftime('%c', time.localtime(time.time())))

    args = parser.parse_args()
    runner = Runner(args)
    runner.run()
