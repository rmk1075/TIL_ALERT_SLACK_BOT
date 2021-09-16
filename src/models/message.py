class Message:
    def __init__(self, **kwargs):
        self.__user = kwargs['user']
        self.__text = kwargs['text']
        self.__ts = kwargs['ts']

        # self.__crtnDate
        # self.__chgDate