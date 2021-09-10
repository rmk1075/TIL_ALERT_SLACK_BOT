import sys
import json

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
