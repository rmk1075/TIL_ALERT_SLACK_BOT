import sys
import json
import pathlib

class Slack:
    def __init__(self, **kwargs):
        self.__config_path = kwargs["config_path"]
        self.__config = self._load_file(self.__config_path)
        if self.__config == None:
            raise RuntimeError()

        self._url = self.__config["url"]
        self._bot = self.__config["bot"]
        self._channel_name = self.__config["channel_name"]
        self._token_info = self.__config["token_info"]

        self._token = self._load_file(str(pathlib.Path(__file__).parent.parent.absolute()) + self._token_info["path"])[self._token_info["name"]]

    def _load_token(self, token_path: str, token_name: str):
        tokens = []
        with open(token_path, 'r') as token_json:
            tokens = json.load(token_json)

        # token_name validation
        if token_name not in tokens.keys():
            sys.stderr.write(f"Wrong token name is given. - {token_name}\n")
            return None

        return tokens[token_name]

    def _load_file(self, file_path: str):
        try:
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        except Exception as e:
            sys.stderr.write(f"Failed to load file {file_path}.\n")
            sys.stderr.write(f"error log - {e}\n")
            return None

    @property
    def url(self):
        return self._url

    @property
    def token(self):
        return self._token

    @property
    def channel_name(self):
        return self._channel_name
