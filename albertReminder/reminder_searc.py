import os
import urllib

'''-------------------------------------------------------------------------------'''
# 구글 API
'''-------------------------------------------------------------------------------'''
## 라이브러리 호출
from google_auth_oauthlib.flow import InstalledAppFlow


## 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로 연결
gcreds_filename = 'C:/Project/albertReminder/gcredentials.json'


## 사용 권한 지정
SCOPES = ['https://www.googleapis.com/auth/calendar']


## 새로운 창에서 로그인하여 인증 정보 얻기
flow = InstalledAppFlow.from_client_secrets_file(gcreds_filename, SCOPES)
gcreds = flow.run_local_server(port=0)


##캘린더 일정 가져오기
from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials = gcreds)





'''----------------------------------------------------------------------------------'''
#발화파라미터 얻기
'''----------------------------------------------------------------------------------'''
##라이브러리 호출
from flask import Flask, request, json
from datetime import date



##기능 변수 정의
app = Flask(__name__)

commonResponse = {
    'version' : '2.0',
    'resultCode' : 'OK',
    'output' : {}
}

def getUtteranceParameter ():
    data = request.get_json()
    return data['action']['parameters']



##연결?
@app.route('/')
def index():
    return 'Hello Flask'

@app.route('/info', methods=['POST'])
def info():
    data = request.get_json()
    print(data['test'])
    response = commonResponse
    response['output']['name'] = 'napier'
    return json.dumps(response)




'''---------------------------------------------------------------'''
#캘린더 스케쥴 불러오기
'''---------------------------------------------------------------'''
category = []
page_token = None

while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()


'''------------------------------------------------------------------------'''
# 특정 일정 검색
'''------------------------------------------------------------------------'''


@app.route('/reminder/searchSchedule', methods =['POST'])
def searchSchedule():
    utteranceParameter = getUtteranceParameter()

    ##기본 변수 설정
    response = commonResponse
    response['output']['existYn'] = 'N'