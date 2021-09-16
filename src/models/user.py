class User:
    def __init__(self, **kwargs):
        self.__id = kwargs['id']
        self.__name = kwargs['name']
        self.__deleted = kwargs['deleted']
        self.__real_name = kwargs['real_name']
        # self.__email = kwargs['email']

        # self.__count
        # self.__crtnDate
        # self.__chgDate
    
    @property
    def id(self):
        return self.__id

    @property
    def real_name(self):
        return self.__real_name