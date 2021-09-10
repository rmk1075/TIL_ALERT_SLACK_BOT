class ApiException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.error_log(message)

    # api 요청에서 에러발생 시 에러 로그 생성하고 시스템 종료하는 함수
    def error_log(self, message: str):
        # TODO: error_log_path hardcoding
        error_log_path = '../../log/error_log/log'
        with open(error_log_path, 'a') as error_log_file:
            error_log_file.write(message)
            print(message)