import os
import json
import unittest

from src.slack import Slack

class TestSlack(unittest.TestCase):
    def setUp(self):
        # craete token file
        self.token = {'token': 'DUMMY_TOKEN'}

        self.token_path = '/usr/app/tests/token.json'
        if not os.path.isfile(self.token_path):
            with open(self.token_path, 'w') as token_file:
                json.dump(self.token, token_file)

        # create config file
        self.config = {
                    "url": "https://slack.com/api/",
                    "bot": {
                        "id": "DUMMY"
                    },
                    "conversation_name": "Channel",
                    "token_info": {
                        "path": self.token_path,
                        "name": "token"
                    }
                }

        self.config_path = '/usr/app/tests/test_config.json'
        with open(self.config_path, "w") as config_file:
            json.dump(self.config, config_file)

        # craete Slack object
        self.slack = Slack(config_path=self.config_path)

    def test_init(self):
        self.assertEqual(self.config["url"], self.slack.url)
        self.assertEqual(self.token['token'], self.slack.token)
        self.assertEqual(self.config['conversation_name'], self.slack.conversation_name)

    def test_load_file(self):
        self.assertEqual(self.config, self.slack._load_file(self.config_path))

    def tearDown(self):
        for file_path in [self.token_path, self.config_path]:
            if os.path.isfile(file_path):
                os.remove(file_path)