import os
import unittest

from src.slack import Slack

class TestSlack(unittest.TestCase):
    def setUp(self):
        token_path = os.path.abspath('../') + '/resources/token.json'
        token_name = 'token'
        channel_name = 'channel_test'

        self.slack = Slack(token_path=token_path, token_name=token_name, channel_name=channel_name)

    def test_load_token(self):
        self.assertFalse(self.slack.token == None)