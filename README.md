# TIL_ALERT_SLACK_BOT

## branch v1.0

- 원하는 메세지를 slack 채널에 전송하는 메세지 봇

- python + 슬랙 api + crontab

- 사용한 슬랙 api

  - user.info

  - conversations.list

  - conversations.history

  - chat.postMessage

1. Slack app 생성 및 workspace 연동 (<https://jammdev.tistory.com/17>)

2. python으로 Slack bot 만들기 (<https://jammdev.tistory.com/19>)

3. crontab 등록하여 자동실행하기 (<https://jammdev.tistory.com/20>)

4. 함수 생성하여 기능 나누기 + til 메세지 날짜 체크 로직 추가

## branch v2.0

1. docker 기반 개발 환경 설정

2. argparser 사용하여 argument 설정 및 default 값 지정

3. class 구현하여 1차 refactoring 진행

4. config 파일 적용 및 file path 오류 해결
