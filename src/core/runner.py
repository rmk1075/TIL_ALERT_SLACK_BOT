import sys
import time
import datetime

from src.slack import Slack
from src.api.api import Api
from src.api.api import ApiHandler

from src.models.user import User
from src.models.message import Message

class Runner:
    def __init__(self, args):
        self._slack = Slack(config_path=args.config_path)
        self._api = Api(url=self._slack.url)
        self._api_handler = ApiHandler(api=self._api, token=self._slack.token)

        self._conversation_id = self.get_conversation_id()

    def get_conversation_id(self):
        conversation_id = self._api_handler.get_conversation_id(self._slack.conversation_name)
        return conversation_id

    def get_user_info(self, user_id):
        user_info = self._api_handler.get_user_info(user_id)
        return user_info

    def get_user_list(self, member_list):
        user_list = []
        for member in member_list:
            user_info = self.get_user_info(member)
            if user_info["is_bot"]:
                continue
            # user = User(id=user_info["id"], name=user_info["name"], real_name=user_info["real_name"], deleted=user_info["deleted"], email=user_info["profile"]["email"])
            user = User(id=user_info["id"], name=user_info["name"], real_name=user_info["real_name"], deleted=user_info["deleted"])
            user_list.append(user)
        return user_list

    def post_message(self, message):
        self._api_handler.post_message(self._conversation_id, message)

    def parse_conversation(self, conversation_list, user_list):
        message_list = []
        target_names = []
        for conversation in conversation_list:
            user_id = conversation["user"]
            for user in user_list:
                if user.id == user_id:
                    message_list.append(Message(user=conversation["user"], text=conversation["text"], ts=conversation["ts"]))
                    target_names.append(user.real_name)
                    break
        return message_list, target_names

    def run(self):
        # get member list
        member_list = self._api_handler.get_conversations_members(conversation_id=self._conversation_id)
        
        # get user list
        user_list = self.get_user_list(member_list=member_list)

        # oldest 시간 구하기 (현재 시간에서 1day를 빼고 계산)
        oldest = time.mktime((datetime.datetime.now() - datetime.timedelta(days = 1)).timetuple())
        conversation_list = self._api_handler.get_conversations_history(self._conversation_id, oldest)

        message_list, target_names = self.parse_conversation(conversation_list=conversation_list, user_list=user_list)

        user_cnt = len(target_names)
        user_names = ''
        for target_name in target_names:
            user_names += target_name + ', '
        message = f'금일 til을 작성한 인원은 {user_names}총 {user_cnt}명 입니다.\n오늘 하루도 수고하셨습니다.'

        # 메세지 전송
        if self._api_handler.post_message(self._conversation_id, message) == None:
            sys.stderr.write("Failed to post message")
            sys.exit(-1)
        print(message)
