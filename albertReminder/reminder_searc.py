#-*-coding:utf-8-*-

##라이브러리 호출
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, json
import datetime
from datetime import date
import os.path
import urllib
import dateutil
import pickle

app = Flask(__name__)

commonResponse = {
    'version': '2.0',
    'resultCode': 'OK',
    'output': {}
}

from google_auth_oauthlib.flow import InstalledAppFlow

gcreds_filename = 'C:/Project/albertReminder/gcredentials.json'


## 사용 권한 지정
SCOPES = ['https://www.googleapis.com/auth/calendar']


## 새로운 창에서 로그인하여 인증 정보 얻기(한번만 하면 됨)
gcreds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        gcreds = pickle.load(token)
if not gcreds or not gcreds.valid:
    if gcreds and gcreds.expired and gcreds.refresh_token:
        gcreds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(gcreds_filename, SCOPES)
        ### 포트는 등록한 (localhost:숫자)url의 숫자로 설정
        gcreds = flow.run_local_server(port=5500)
    with open('token.pickle', 'wb') as token:
        pickle.dump(gcreds, token)



##캘린더 일정 가져오기
service = build('calendar', 'v3', credentials=gcreds)



#발화파라미터얻기
def getUtteranceParameter () :
    data = request.get_json()
    return data['action']['parameters']


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

@app.route('/reminder/searchSchedule', methods=['POST'])
def searchSchedule():
    utteranceParameter = getUtteranceParameter()
    searchName = utteranceParameter['schedule']['value']
    print(searchName)

    response = commonResponse
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'
    time_max = (datetime.date.today()+datetime.timedelta(days=7)).isoformat() + 'T23:59:59+09:00'


    #캘린더 리스트 목록뽑기
    category = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry['summary'])
            category.append(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break


    # 전체 일정 불러오기
    private = []
    private_all =  []
    public = []
    public_all = []

    for i in range(len(calendar_list['items'])):
        if calendar_list['items'][i]['summary'] == "개인일정":
            calendar_id = calendar_list['items'][i]['id']
            is_single_events = True
            orderby = 'startTime'
            events_result = service.events().list(calendarId=calendar_id,
                                                  timeMin=time_min,
                                                  timeMax=time_max,
                                                  singleEvents=is_single_events,
                                                  orderBy=orderby
                                                  ).execute()
            items = events_result.get('items')
            for j in range(len(items)):
                time = items[j].get('start')
                todo = items[j].get('summary')
                if 'dateTime' in time:
                    T = time['dateTime']
                    Time = T[5:7] + "월 " + T[8:10] + "일 " +T[11:13] + "시 " + T[14:16] + "분"
                    private.append(Time + "에 " + todo)
                    private.sort()
                else:
                    T = time.values()
                    Time = T[19:21] + "월 " + T[22:24] + "일 "
                    print(Time)
                    private_all.append(todo)


        else:
            calendar_id = calendar_list['items'][i]['id']
            is_single_events = True
            orderby = 'startTime'
            events_result = service.events().list(calendarId=calendar_id,
                                                  timeMin=time_min,
                                                  timeMax=time_max,
                                                  singleEvents=is_single_events,
                                                  orderBy=orderby
                                                  ).execute()
            items = events_result.get('items')
            for j in range(len(items)):
                time = items[j].get('start')
                todo = items[j].get('summary')
                if 'dateTime' in time:
                    T = time['dateTime']
                    Time = T[5:7] + "월 " + T[8:10] + "일 " +T[11:13] + "시 " + T[14:16] + "분"
                    public.append(Time + "에 " + todo)
                    public.sort()
                else:
                    private_all.append(todo)


    print("개인 일정")
    print(private)
    print("개인 종일 일정")
    print(private_all)
    print("업무 일정")
    print(public)
    print("업무 종일 일정")
    print(public_all)



    response['output']['searchName'] = searchName
    response['output']['existYn'] = 'N'

    response['output']['privatePart'] = private
    response['output']['privateAll'] = private_all
    response['output']['publicPart'] = public
    response['output']['publicAll'] = public_all

    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
