import os
import sys
import datetime
import time
import json
import argparse
import pathlib

from typing import List

from src.slack import Slack
from src.api.api import Api
from src.api.api import ApiHandler

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--alert", help="excute alert mode", action="store_true")
parser.add_argument("-c", "--config_path", help="path of config file", type=str, default=str(pathlib.Path(__file__).parent.parent.absolute()) + "usr/app/config/config.json")

if __name__ == "__main__":
    # 현재 시간 log
    print(time.strftime('%c', time.localtime(time.time())))

    args = parser.parse_args()
    config_path = args.config_path

    # init Slack
    slack = Slack(config_path=config_path)
    if slack == None:
        sys.stderr.write("Failed to init Slack instance.\n")
        sys.exit(-1)

    # init Api
    api = Api(url=slack.url)
    if api == None:
        sys.stderr.write("Failed to init Api instance.\n")
        sys.exit(-1)

    # create ApiHandler
    api_handler = ApiHandler(api=api, token=slack.token)
    if api_handler == None:
        sys.stderr.write("Failed to create ApiHandler instance.\n")
        sys.exit(-1)

    # conversations.list api를 사용하여서 slack 대화 채널 id 조회
    channel_id = api_handler.get_channel_id(slack.channel_name)
    if channel_id == None:
        sys.stderr.write("Failed to get channel_id\n")
        sys.exit(-1)

    # bot이 전송할 메세지 생성
    # argument '--alert' 사용시 alert 모드로 실행
    if args.alert:
        print("alert mode")
        message = f'현재시간 {datetime.datetime.now().strftime("%H:%M")}입니다.\n아직 til을 작성하지 않으신 분은 빠르게 작성해주세요.'
    else:
        print("counting mode")

        # conversations.history api를 사용하여서 til 작성한 user들의 id 조회
        user_list = api_handler.get_user_list(channel_id)
        if user_list == None:
            sys.stderr.write("Failed to get user_list\n")
            sys.exit(-1)

        # user_list의 user id를 통해서 user 이름 조회
        user_names_list = api_handler.get_user_names(channel_id, user_list)
        if user_names_list == None:
            sys.stderr.write("Failed to get user_names\n")
            sys.exit(-1)
        user_cnt = len(user_names_list)

        user_names = ''
        if 0 < user_cnt:
            for user_name in user_names_list:
                user_names += user_name + ', '

        message = f'금일 til을 작성한 인원은 {user_names}총 {user_cnt}명 입니다.\n오늘 하루도 수고하셨습니다.'

    # 메세지 전송
    if api_handler.post_message(channel_id, message) == None:
        sys.stderr.write("Failed to post message")
        sys.exit(-1)
    print(message)