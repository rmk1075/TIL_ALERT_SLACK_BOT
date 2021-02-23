import sys, datetime
import json
import requests
from pandas import json_normalize

# slack bot token 불러오기
# json으로 저장한 token.json 파일을 읽어와서 token key 조회
parent_path = '/Users/jeonjaemin/Desktop/git_repos/TIL_ALERT_SLACK_BOT'
slack_token_path = parent_path + '/resource/token.json'
with open(slack_token_path, 'r') as token_json:
    slack_dict = json.load(token_json)

slack_token = slack_dict['token']

# 슬랙 채널 조회하기
# Bot이 활동할 채널의 이름
channel_name = "til"

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
error_log_path = parent_path + '/log/error_log.log'
if not response.json()['ok']:
    with open(error_log_path, 'a') as error_log_file:
        error_log_message = f'[error][conversation.list][{datetime.datetime.now()}] call \'conversation.list\' api error. \n[error message]{response.json()["error"]}\n'
        error_log_file.write(error_log_message)
        sys.exit(1)


# 채널 리스트
channel_list = json_normalize(response.json()['channels'])
channel_id = list(channel_list.loc[channel_list['name'] == channel_name, 'id'])[0]

print(channel_name, channel_id)


# bot으로 메시지 전송
message = f'test message'

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
error_log_path = parent_path + '/log/error_log.log'
if not response.json()['ok']:
    with open(error_log_path, 'a') as error_log_file:
        error_log_message = f'[error][chat.postMessage][{datetime.datetime.now()}] call \'chat.postMessage\' api error. \n[error message]{response.json()["error"]}\n'
        error_log_file.write(error_log_message)
        sys.exit(1)