import os
import sys
import datetime
import time
import json
import requests
import re
import argparse

from pandas import json_normalize
from typing import List

# api 요청에서 에러발생 시 에러 로그 생성하고 시스템 종료하는 함수
def error_log(response: requests.models.Response, api_name: str):
    # TODO: error_log_path
    # error_log_path = parent_path + '/log/error_log.log'
    error_log_path = '../log/error_log/log'
    if not response.json()['ok']:
        with open(error_log_path, 'a') as error_log_file:
            error_log_message = f'[error][{api_name}][{datetime.datetime.now()}] call \'{api_name}\' api error. \n[error message]{response.json()["error"]}\n'
            error_log_file.write(error_log_message)

            print(error_log_message)
            return True
    return False

# slack bot이 활동할 slack 채널 id 반환하는 함수
def find_channel_id(slack_token: str, channel_name: str):
    # 슬랙 채널 조회하기
    # 채널 조회 api method (conversations.list)
    # https://api.slack.com/methods/conversations.list 확인
    URL = 'https://slack.com/api/conversations.list'

    # 파라미터
    # required args - token, accepted content type
    params = {
        'token': slack_token,
        'Content-Type': 'application/x-www-form-urlencoded'
        }

    # API 호출
    response = requests.get(URL, params=params)

    # response error check
    if error_log(response, 'conversations.list'):
        print('api error')
        sys.exit(1)

    # 채널 리스트
    channel_list = json_normalize(response.json()['channels'])
    channel_id = list(channel_list.loc[channel_list['name'] == channel_name, 'id'])[0]

    print('채널 이름: ', channel_name, '채널 id:', channel_id)

    return channel_id

# til 작성한 사용자들을 list로 반환하는 함수
def find_user_list(slack_token: str, channel_id: str):
    user_list = set([])

    # 대화 히스토리 api
    # https://api.slack.com/methods/conversations.history
    URL = 'https://slack.com/api/conversations.history'

    # oldest 시간 구하기 (현재 시간에서 1day를 빼고 계산)
    oldest = time.mktime((datetime.datetime.now() - datetime.timedelta(days = 1)).timetuple())

    # 파라미터
    params = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'token': slack_token,
        'channel': channel_id,
        'oldest': oldest
    }

    response = requests.get(URL, params=params)

    if error_log(response, 'conversations.history'):
        print('api error')
        sys.exit(1)
    
    # 어제 날짜 확인을 위한 patter 생성
    yesterday = datetime.date.today() - datetime.timedelta(1)
    pattern = re.compile(yesterday.strftime('\\[%Y.%m.%d\\]') + '*')

    # 메세지 확인
    # 1. slack bot 제외 ('U01NKV5PPCP')
    # 2. 날짜 확인
    for message in response.json()['messages']:
        if message['user'] == 'U01NKV5PPCP':
            continue

        if pattern.match(message['text']):
            user_list.add(message['user'])

    return list(user_list)

# user_id에 해당하는 사용자의 이름을 str로 반환하는 함수
def find_user_name(slack_token: str, channel_id: str, user_id: str):
    # 사용자 정보 조회 api
    # https://api.slack.com/methods/users.info
    URL = 'https://slack.com/api/users.info'

    # 파라미터
    params = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'token': slack_token,
        'user': user_id,
    }

    response = requests.get(URL, params=params)

    if error_log(response, 'user.info'):
        print('api error')
        sys.exit(1)
    
    return response.json()['user']['real_name']

# til 작성한 사용자들의 이름을 str, 숫자를 int로 반환하는 함수
def find_user_names(slack_token: str, channel_id: str, user_list: List[str]):
    user_names, user_cnt = '', 0
    for user_id in user_list:
        user_names += find_user_name(slack_token, channel_id, user_id) + ', '
        user_cnt += 1
    
    return user_names, user_cnt

# slack 채널에 메시지 작성하는 함수
def post_message(slack_token, channel_id, message):
    # 메시지 전송 api method (chat.postMessage)
    # https://api.slack.com/methods/chat.postMessage
    URL = 'https://slack.com/api/chat.postMessage'

    # 파라미터
    data = {
        'Context_Type': 'application/x-www-form-urlencoded',
        'token': slack_token,
        'channel': channel_id,
        'text': message
    }

    # API 호출
    response = requests.post(URL, data=data)

    # response error check
    if error_log(response, 'chat.postMessage'):
        print('api error')
        sys.exit(1)

    print(message)


class Slack:
    def __init__(self, **kwargs):
        self._token_path = kwargs["token_path"]
        self._token_name = kwargs["token_name"]
        self._token = None
        self._channel_name = kwargs["channel_name"]

        self._token = self._load_token(self._token_path, self._token_name)
        if self._token == None:
            return None

    def _load_token(self, token_path: str, token_name: str):
        tokens = []
        with open(token_path, 'r') as token_json:
            tokens = json.load(token_json)

        # token_name validation
        if token_name not in tokens.keys():
            sys.stderr.write(f"Wrong token name is given. - {token_name}\n")
            return None

        return tokens[token_name]

    @property
    def token(self):
        return self._token

    @property
    def channel_name(self):
        return self._channel_name


class Api:
    def __init__(self, **kwargs):
        self._url = kwargs["url"]

    @property
    def url(self):
        return self._url

    def request(self, method: str, params: dict):
        # API 호출
        response = requests.get(self._url + method, params=params)
        return response


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--token_path", help="path of token.json file", type=str, default='../resource/token.json')
parser.add_argument("-t", "--token_name", help="name of token", type=str, default='test_token')
# parser.add_argument("-t", "--token_name", help="name of token", type=str, default='token')
parser.add_argument("-c", "--channel_name", help="name of slack channel", type=str, default='til')
# parser.add_argument("-c", "--channel_name", help="name of slack channel", type=str, default='today-i-learned')
parser.add_argument("-u", "--url", help="api server url", type=str, default='https://slack.com/api/')

if __name__ == "__main__":
    # 현재 시간 log
    print(time.strftime('%c', time.localtime(time.time())))

    args = parser.parse_args()
    token_path = args.token_path
    token_name = args.token_name
    channel_name = args.channel_name
    url = args.url

    # init Slack
    slack = Slack(token_path=token_path, token_name=token_name, channel_name=channel_name)
    if not slack:
        sys.stderr.write("Failed to init Slack instance.\n")
        sys.exit(-1)

    # init Api
    api = Api(url=url)
    if not api:
        sys.stderr.write("Failed to inint Api instance.\n")
        sys.exit(-1)

    # conversations.list api를 사용하여서 slack 대화 채널 id 조회
    channel_id = find_channel_id(slack.token, slack.channel_name)


    # bot이 전송할 메세지 생성
    # args의 값에 따라서 메세지 내용 변경
    args = sys.argv[0:]
    if len(args) != 1 and args[1] == '0':
        message = f'현재시간 {datetime.datetime.now().strftime("%H:%M")}입니다.\n아직 til을 작성하지 않으신 분은 빠르게 작성해주세요.'
    else:
        # conversations.history api를 사용하여서 til 작성한 user들의 id 조회
        # user_list = find_user_list(slack_token, channel_id)
        user_list = find_user_list(slack.token, channel_id)

        print(user_list)

        # user_list의 user id를 통해서 user 이름 조회
        # user_names, user_cnt = find_user_names(slack_token, channel_id, user_list)
        user_names, user_cnt = find_user_names(slack.token, channel_id, user_list)

        print(user_names)
        print(user_cnt)

        message = f'금일 til을 작성한 인원은 {user_names}총 {user_cnt}명 입니다.\n오늘 하루도 수고하셨습니다.'


    # 메세지 전송
    # post_message(slack_token, channel_id, message)
    post_message(slack.token, channel_id, message)
