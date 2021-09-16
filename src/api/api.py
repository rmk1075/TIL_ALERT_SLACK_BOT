import sys
import re
import time
import requests
import datetime

from pandas import json_normalize
from typing import List

from src.exceptions.api_exception import ApiException

class Api:
    def __init__(self, **kwargs):
        self._url = kwargs["url"]

    @property
    def url(self):
        return self._url

    # API 호출
    def request(self, method: str, params: dict):
        response = requests.get(method, params=params)
        return response

    # request api
    def api_request(self, method: str, params: dict):
        try:
            response = self.request(method=self._url + method, params=params)
            if not response.json()['ok']:
                raise ApiException(f'[error][{method}][{datetime.datetime.now()}] call \'{method}\' api error. \n[error message]{response.json()["error"]}\n')
            return response                
        except ApiException as e:
            print(f"Api Exception occurred: {e}")
            return None
        except Exception as e:
            print(f"error occured : {e}")
            return None


class ApiHandler:
    def __init__(self, api: Api, token: str):
        self.__api = api
        self.__token = token

    def get_conversation_id(self, conversation_name: str):
        # 파라미터
        method = 'conversations.list'
        params = {
            'token': self.__token,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        conversations = self.__api.api_request(method=method, params=params)
        if not conversations:
            sys.stderr.write("Failed to get conversations list\n")
            return None

        # 채널 리스트
        conversation_list = json_normalize(conversations.json()['channels'])
        conversation_id = list(conversation_list.loc[conversation_list['name'] == conversation_name, 'id'])[0]

        print('채널 이름: ', conversation_name, '채널 id:', conversation_id)

        return conversation_id

    def get_conversations_members(self, conversation_id: str):
        method = 'conversations.members'
        params = {
            'token': self.__token,
            'channel': conversation_id
        }

        members = self.__api.api_request(method=method, params=params)
        if not members:
            sys.stderr.write("Failed to get members\n")
            return None

        return members.json()["members"]

    def get_user_info(self, user_id: str):
        method = 'users.info'
        params = {
            'token': self.__token,
            'user': user_id,
            'include_locale': True
        }

        user_info = self.__api.api_request(method=method, params=params)
        if not user_info:
            sys.stderr.write("Failed to get user\n")
            return None

        return user_info.json()["user"]

    def get_conversations_history(self, conversation_id: str, oldest: float):
        # 파라미터
        method = 'conversations.history'
        params = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'token': self.__token,
            'channel': conversation_id,
            'oldest': oldest
        }

        conversations_history = self.__api.api_request(method=method, params=params)
        if not conversations_history:
            sys.stderr.write(f"Failed to get {method}.\n")
            return None

        # 어제 날짜 확인을 위한 patter 생성
        yesterday = datetime.date.today() - datetime.timedelta(1)
        pattern = re.compile(yesterday.strftime('\\[%Y.%m.%d\\]') + '*')

        # 메세지 확인
        # 날짜 포맷 확인 [yyyy.mm.dd]
        conversation_list = []
        for message in conversations_history.json()['messages']:
            if pattern.match(message['text']):
                conversation_list.append(message)

        return conversation_list

    def post_message(self, conversation_id, message: str):
        # 파라미터
        method = 'chat.postMessage'
        params = {
            'Context_Type': 'application/x-www-form-urlencoded',
            'token': self.__token,
            'channel': conversation_id,
            'text': message
        }

        response = self.__api.api_request(method=method, params=params)
        if not response:
            sys.stderr.write(f"Failed to {method}.\n")
            return None
        else:
            return message
