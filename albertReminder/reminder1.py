#-*-coding:utf-8-*-
from flask import Flask, request, json
import datetime
from datetime import date
import os
import urllib

app = Flask(__name__)

commonResponse = {
    'version': '2.0',
    'resultCode': 'OK',
    'output': {}
}

from google_auth_oauthlib.flow import InstalledAppFlow

# 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로
creds_filename = 'C:/Users/user/python test/gcredentials.json'

# 사용 권한 지정
# https://www.googleapis.com/auth/calendar	               캘린더 읽기/쓰기 권한
# https://www.googleapis.com/auth/calendar.readonly	       캘린더 읽기 권한
SCOPES = ['https://www.googleapis.com/auth/calendar']

# 파일에 담긴 인증 정보로 구글 서버에 인증하기
# 새 창이 열리면서 구글 로그인 및 정보 제공 동의 후 최종 인증이 완료됩니다.
flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
creds = flow.run_local_server(port=0)

from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials=creds)



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

@app.route('/reminder/answerallschedule', methods=['POST'])
def answerallschedule():
    utteranceParameter = getUtteranceParameter()
    if utteranceParameter['day']['value']:
        Day = utteranceParameter['day']['value']
    else: Day = None
    if utteranceParameter['ymonth']['value'] :
        Ymonth = utteranceParameter['ymonth']['value'][14:]
    else: Ymonth = None
    if utteranceParameter['mday']['value'] :
        Mday = utteranceParameter['mday']['value'][12:]
    else: Mday = None
    print(Day, Ymonth, Mday)

    response = commonResponse
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'
    time_max = today + 'T23:59:59+09:00'

    if Day == "BID_DT_DAY.TODAY":
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'
    elif Day == "BID_DT_DAY.TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '내일'
    elif Day == "BID_DT_DAY.A_TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '모레'
    elif Day == "BID_DT_DAY.YESTERDAY":
        time_min = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '어제'
    elif Day == "BID_DT_DAY.B_YESTERDAY":
        time_min = (datetime.date.today() + datetime.timedelta(days=-2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today() + datetime.timedelta(days=-2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '그제'
    elif Mday and Ymonth == None :
        defineday = date(datetime.date.today().year, datetime.date.today().month, int(Mday)).isoformat()
        time_min = defineday + 'T00:00:00+09:00'
        time_max = defineday + 'T23:59:59+09:00'
        response['output']['returndate'] = str(datetime.date.today().month) + '월 ' + str(Mday) + '일'
    elif Mday and Ymonth :
        defineday = date(datetime.date.today().year, int(Ymonth), int(Mday)).isoformat()
        time_min = defineday + 'T00:00:00+09:00'
        time_max = defineday + 'T23:59:59+09:00'
        response['output']['returndate'] = str(Ymonth) + '월 ' + str(Mday) + '일'
    else:
        today = datetime.date.today().isoformat()
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'


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


    #카테고리 3개 다 있는지 확인
    if "개인일정" in category and "업무일정" in category and "소지품" in category:
        categoryexist = "Y"
    else:
        categoryexist = "N"
    print(categoryexist)

    # 전체 일정 불러오기(소지품, 스케쥴은 구분)
    belongings = []
    schedule = []

    for i in range(len(calendar_list['items'])):
        if calendar_list['items'][i]['summary'] == "소지품":
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
                todo = items[j].get('summary')
                belongings.append(todo)

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
                    Time = T[11:13] + "시 " + T[14:16] + "분"
                    schedule.append(Time + "에는 " + todo)
                    schedule.sort()
                else:
                    schedule.append(todo)


    print(belongings)
    print(schedule)



    response['output']['existYn'] = 'N'

    if  schedule and not belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = []
    elif not schedule and belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = []
        response['output']['belongings'] = belongings
    elif schedule and belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = belongings
    else:
        response['output']['existYn'] = 'N'
        response['output']['schedule'] = []
        response['output']['belongings'] = []

    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
