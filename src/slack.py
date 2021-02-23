import sys, datetime, time
import json
import requests
from pandas import json_normalize


# api 요청에서 에러발생 시 에러 로그 생성
def error_log(response: requests.models.Response, api_name: str) -> bool:
    error_log_path = parent_path + '/log/error_log.log'
    if not response.json()['ok']:
        with open(error_log_path, 'a') as error_log_file:
            error_log_message = f'[error][{api_name}][{datetime.datetime.now()}] call \'{api_name}\' api error. \n[error message]{response.json()["error"]}\n'
            error_log_file.write(error_log_message)
            return True
    return False


# til 작성한 사용자들을 list로 반환하는 함수
def find_users(slack_token: str, channel_id: str) -> list[str]:
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
    
    for message in response.json()['messages']:
        if message['user'] == 'U01NKV5PPCP':
            continue
        user_list.add(message['user'])

    return list(user_list)


# user_id에 해당하는 사용자의 이름을 str로 반환하는 함수
def find_user(slack_token: str, channel_id: str, user_id: str) -> str:
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
def find_names(slack_token: str, channel_id: str, user_list: list[str]) -> (str, int):
    user_names, user_cnt = '', 0
    for user_id in user_list:
        user_names += find_user(slack_token, channel_id, user_id) + ', '
        user_cnt += 1
    
    return user_names, user_cnt


# slack bot token 불러오기
# json으로 저장한 token.json 파일을 읽어와서 token key 조회
parent_path = '/Users/jeonjaemin/Desktop/git_repos/TIL_ALERT_SLACK_BOT'
slack_token_path = parent_path + '/resource/token.json'
with open(slack_token_path, 'r') as token_json:
    slack_dict = json.load(token_json)

slack_token = slack_dict['token']

# 슬랙 채널 조회하기
# Bot이 활동할 채널의 이름
# channel_name = "til"
channel_name = 'today-i-learned'

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

print(channel_name, channel_id)


# bot이 전송할 메세지 생성
# args의 값에 따라서 메세지 내용 변경
args = sys.argv[0:]
if len(args) != 1 and args[1] == '0':
    message = f'현재시간 {datetime.datetime.now().strftime("%H:%M")}입니다.\n아직 til을 작성하지 않으신 분은 빠르게 작성해주세요.'
else:
    # til 작성한 user들의 id 조회
    user_list = find_users(slack_token, channel_id)

    print(user_list)

    # user_list의 user id를 통해서 user 이름 조회
    user_names, user_cnt = find_names(slack_token, channel_id, user_list)

    message = f'금일 til을 작성한 인원은 {user_names}총 {user_cnt}명 입니다.\n오늘 하루도 수고하셨습니다.'

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

