import sys, datetime, time
import json
import requests
import re
from pandas import json_normalize

# api 요청에서 에러발생 시 에러 로그 생성하고 시스템 종료하는 함수
def error_log(response: requests.models.Response, api_name: str) -> bool:
    error_log_path = parent_path + '/log/error_log.log'
    if not response.json()['ok']:
        with open(error_log_path, 'a') as error_log_file:
            error_log_message = f'[error][{api_name}][{datetime.datetime.now()}] call \'{api_name}\' api error. \n[error message]{response.json()["error"]}\n'
            error_log_file.write(error_log_message)

            print(error_log_message)
            return True
    return False

# slack bot이 활동할 slack 채널 id 반환하는 함수
def find_channel_id(slack_token: str, channel_name: str) -> str:
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
def find_user_list(slack_token: str, channel_id: str) -> list[str]:
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
def find_user_name(slack_token: str, channel_id: str, user_id: str) -> str:
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
def find_user_names(slack_token: str, channel_id: str, user_list: list[str]) -> (str, int):
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

if __name__ == "__main__":
    # 현재 시간 log
    print(time.strftime('%c', time.localtime(time.time())))

    # slack bot token 불러오기
    # json으로 저장한 token.json 파일을 읽어와서 token key 조회
    parent_path = '/Users/jeonjaemin/Desktop/git_repos/TIL_ALERT_SLACK_BOT'
    slack_token_path = parent_path + '/resource/token.json'
    with open(slack_token_path, 'r') as token_json:
        slack_dict = json.load(token_json)

    # api 사용을 위한 token 선택 - 'token', 'test_token'
    slack_token = slack_dict['test_token']
    # slack_token = slack_dict['token']

    # Bot이 활동할 채널의 이름
    channel_name = "til"
    # channel_name = 'today-i-learned'


    # conversations.list api를 사용하여서 slack 대화 채널 id 조회
    channel_id = find_channel_id(slack_token, channel_name)


    # bot이 전송할 메세지 생성
    # args의 값에 따라서 메세지 내용 변경
    args = sys.argv[0:]
    if len(args) != 1 and args[1] == '0':
        message = f'현재시간 {datetime.datetime.now().strftime("%H:%M")}입니다.\n아직 til을 작성하지 않으신 분은 빠르게 작성해주세요.'
    else:
        # conversations.history api를 사용하여서 til 작성한 user들의 id 조회
        user_list = find_user_list(slack_token, channel_id)

        print(user_list)

        # user_list의 user id를 통해서 user 이름 조회
        user_names, user_cnt = find_user_names(slack_token, channel_id, user_list)

        print(user_names)
        print(user_cnt)

        message = f'금일 til을 작성한 인원은 {user_names}총 {user_cnt}명 입니다.\n오늘 하루도 수고하셨습니다.'


    # 메세지 전송
    post_message(slack_token, channel_id, message)
