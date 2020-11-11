#-*-coding:utf-8-*-

##라이브러리 호출
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, json
from datetime import date
import os
import urllib

'''-------------------------------------------------------------------------------'''
# 구글 API
'''-------------------------------------------------------------------------------'''
## 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로 연결
gcreds_filename = 'C:/Project/albertReminder/gcredentials.json'


## 사용 권한 지정
SCOPES = ['https://www.googleapis.com/auth/calendar']


## 새로운 창에서 로그인하여 인증 정보 얻기
flow = InstalledAppFlow.from_client_secrets_file(gcreds_filename, SCOPES)
gcreds = flow.run_local_server(port=5500)


##캘린더 일정 가져오기
from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials=gcreds)





'''----------------------------------------------------------------------------------'''
#발화파라미터 얻기
'''----------------------------------------------------------------------------------'''
##기능 변수 정의
app = Flask(__name__)

commonResponse = {
    'version': '2.0',
    'resultCode': 'OK',
    'output': {}
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


'''------------------------------------------------------------------------'''
# 특정 일정 검색
'''------------------------------------------------------------------------'''


@app.route('/reminder/searchSchedule', methods=['POST'])
def searchSchedule():


    ## 설정
    utteranceParameter = getUtteranceParameter()
    response = commonResponse
    category = []
    allDay = []
    partTime = []

    '''---------------------------------------------------------------'''
    # 캘린더 스케쥴 불러오기
    '''---------------------------------------------------------------'''
    ## 카테고리 저장
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken = page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry['summary'])
            category.append(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    #for i in range(len(calendar_list['items'])):
    '''-----------------------------------------------------------'''
    #output 설정
    '''-----------------------------------------------------------'''
    schedule = utteranceParameter['schedule']['value']

    response['output']['returnSchedule'] = schedule
    response['output']['existYn'] = 'N'

    ## 종일 스케줄인 경우
    if allDay and not partTime:
        response['output']['existYn'] = 'Y'
        response['output']['returnDate'] = allDay
    ## 시간 설정 스케줄인 경우
    elif not allDay and partTime:
        response['output']['existYn'] = 'Y'
        response['output']['returnDate'] = partTime
    ## 두 가지가 공존할 경우
    else:
        response['output']['existYn'] = 'Y'
        dayTime = allDay + partTime
        response['output']['returnDate'] = dayTime

    return json.dumps(response)


'''------------------------------------------------------------------'''
#포트 연결
'''------------------------------------------------------------------'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)