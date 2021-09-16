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

    # # argument '--alert' 사용시 alert 모드로 실행
    if args.alert:
        print("alert mode")
        message = f'현재시간 {datetime.datetime.now().strftime("%H:%M")}입니다.\n아직 til을 작성하지 않으신 분은 빠르게 작성해주세요.'
        print(message)

        runner.post_message(message=message)
        sys.exit(0)

    runner.run()
