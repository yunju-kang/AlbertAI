#-*-coding:utf-8-*-
from flask import Flask, request, json
import datetime
from datetime import date
import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)

commonResponse = {
    'version': '2.0',
    'resultCode': 'OK',
    'output': {}
}


# 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로
# download credential from google cloud console
gcreds_filename = 'gcredentials.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']

# 파일에 담긴 인증 정보로 구글 서버에 인증하기
# get approval using token

gcreds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        gcreds = pickle.load(token)
if not gcreds or not gcreds.valid:
    if gcreds and gcreds.expired and gcreds.refresh_token:
        gcreds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(gcreds_filename, SCOPES)
        gcreds = flow.run_local_server(port=0)

        #aws에 5501 포트 열기
        # add aws 5501 port
        redirect_uri = 'http://(aws_public_dns_address):5501/'
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    with open('token.pickle', 'wb') as token:
        pickle.dump(gcreds, token)


service = build('calendar', 'v3', credentials=gcreds)


#발화파라미터얻기
#get utterance parameter
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

##기능 1번 전체 일정 검색
##function 1. search all schedule by date
@app.route('/reminder/Answer_AllSchedule', methods=['POST'])
def Answer_AllSchedule():
    utteranceParameter = getUtteranceParameter()
    if 'day' in utteranceParameter:
        Day = utteranceParameter['day']['value']
    else: Day = None
    if 'ymonth' in utteranceParameter:
        Ymonth = utteranceParameter['ymonth']['value'][14:]
    else: Ymonth = None
    if 'mday' in utteranceParameter:
        Mday = utteranceParameter['mday']['value'][12:]
    else: Mday = None
    print(Day, Ymonth, Mday)

    response = commonResponse
    today = datetime.date.today().isoformat()

    if Day == "TODAY":
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'
    elif Day == "TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '내일'
    elif Day == "A_TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '모레'
    elif Day == "YESTERDAY":
        time_min = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '어제'
    elif Day == "B_YESTERDAY":
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
    #get list of calendar schedules
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
    #check wether all category has list
    if "개인 일정" in category and "업무 일정" in category and "소지품" in category:
        categoryexist = "Y"
    else:
        categoryexist = "N"

    # 전체 일정 불러오기(소지품, 스케쥴은 구분)
    # get schedules, belongings list
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

    belongings = '. '.join(belongings)
    schedule = '. '.join(schedule)
    print(belongings)
    print(schedule)



    response['output']['existYn'] = 'N'

    if  schedule and not belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = None
    elif not schedule and belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = None
        response['output']['belongings'] = belongings
    elif schedule and belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = belongings
    else:
        response['output']['existYn'] = 'N'
        response['output']['schedule'] = None
        response['output']['belongings'] = None

    return json.dumps(response)




##기능2번 업무 일정 검색
##function 2. search public schedules
@app.route('/reminder/Answer_BusinessSchedule', methods=['POST'])
def Answer_BusinessSchedule():
    utteranceParameter = getUtteranceParameter()
    if 'day' in utteranceParameter:
        Day = utteranceParameter['day']['value']
    else: Day = None
    if 'ymonth' in utteranceParameter:
        Ymonth = utteranceParameter['ymonth']['value'][14:]
    else: Ymonth = None
    if 'mday' in utteranceParameter:
        Mday = utteranceParameter['mday']['value'][12:]
    else: Mday = None
    print(Day, Ymonth, Mday)

    response = commonResponse
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'
    time_max = today + 'T23:59:59+09:00'

    if Day == "TODAY":
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'
    elif Day == "TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '내일'
    elif Day == "A_TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '모레'
    elif Day == "YESTERDAY":
        time_min = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '어제'
    elif Day == "B_YESTERDAY":
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
    if "개인 일정" in category and "업무 일정" in category and "소지품" in category:
        categoryexist = "Y"
    else:
        categoryexist = "N"

    # 업무 일정 불러오기
    belongings = None
    schedule = []

    for i in range(len(calendar_list['items'])):
        if calendar_list['items'][i]['summary'] != "업무 일정":
            continue
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

    schedule = '. '.join(schedule)
    print(belongings)
    print(schedule)


    response['output']['existYn'] = 'N'

    if schedule :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = belongings

    else:
        response['output']['existYn'] = 'N'
        response['output']['schedule'] = None
        response['output']['belongings'] = belongings

    return json.dumps(response)



##기능3번 개인 일정 검색
@app.route('/reminder/Answer_PersonalSchedule', methods=['POST'])
def Answer_PersonalSchedule():
    utteranceParameter = getUtteranceParameter()
    if 'day' in utteranceParameter:
        Day = utteranceParameter['day']['value']
    else: Day = None
    if 'ymonth' in utteranceParameter:
        Ymonth = utteranceParameter['ymonth']['value'][14:]
    else: Ymonth = None
    if 'mday' in utteranceParameter:
        Mday = utteranceParameter['mday']['value'][12:]
    else: Mday = None
    print(Day, Ymonth, Mday)

    response = commonResponse
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'
    time_max = today + 'T23:59:59+09:00'

    if Day == "TODAY":
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'
    elif Day == "TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '내일'
    elif Day == "A_TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '모레'
    elif Day == "YESTERDAY":
        time_min = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '어제'
    elif Day == "B_YESTERDAY":
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
    if "개인 일정" in category and "업무 일정" in category and "소지품" in category:
        categoryexist = "Y"
    else:
        categoryexist = "N"

    # 개인 일정 불러오기
    belongings = None
    schedule = []

    for i in range(len(calendar_list['items'])):
        if calendar_list['items'][i]['summary'] != "개인 일정":
            continue
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

    schedule = '. '.join(schedule)
    print(schedule)


    response['output']['existYn'] = 'N'

    if schedule :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = belongings

    else:
        response['output']['existYn'] = 'N'
        response['output']['schedule'] = None
        response['output']['belongings'] = belongings

    return json.dumps(response)


##기능4번 소지품 검색
@app.route('/reminder/Answer_Belongings', methods=['POST'])
def Answer_Belongings():
    utteranceParameter = getUtteranceParameter()
    if 'day' in utteranceParameter:
        Day = utteranceParameter['day']['value']
    else: Day = None
    if 'ymonth' in utteranceParameter:
        Ymonth = utteranceParameter['ymonth']['value'][14:]
    else: Ymonth = None
    if 'mday' in utteranceParameter:
        Mday = utteranceParameter['mday']['value'][12:]
    else: Mday = None
    print(Day, Ymonth, Mday)

    response = commonResponse
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'
    time_max = today + 'T23:59:59+09:00'

    if Day == "TODAY":
        time_min = today + 'T00:00:00+09:00'
        time_max = today + 'T23:59:59+09:00'
        response['output']['returndate'] = '오늘'
    elif Day == "TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '내일'
    elif Day == "A_TOMORROW":
        time_min = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=2)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '모레'
    elif Day == "YESTERDAY":
        time_min = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T00:00:00+09:00'
        time_max = (datetime.date.today()+datetime.timedelta(days=-1)).isoformat() + 'T23:59:59+09:00'
        response['output']['returndate'] = '어제'
    elif Day == "B_YESTERDAY":
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
    if "개인 일정" in category and "업무 일정" in category and "소지품" in category:
        categoryexist = "Y"
    else:
        categoryexist = "N"

    # 소지품 불러오기
    belongings = []
    schedule = None

    for i in range(len(calendar_list['items'])):
        if calendar_list['items'][i]['summary'] != "소지품":
            continue
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
                todo = items[j].get('summary')
                belongings.append(todo)

    belongings = '. '.join(belongings)
    print(belongings)


    response['output']['existYn'] = 'N'

    if belongings :
        response['output']['existYn'] = 'Y'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = belongings

    else:
        response['output']['existYn'] = 'N'
        response['output']['schedule'] = schedule
        response['output']['belongings'] = None

    return json.dumps(response)


'''---------------------------------------------------------------------'''
    # 일정 찾기 함수
'''---------------------------------------------------------------------'''

@app.route('/reminder/Answer_SpecificSchedule', methods=['POST'])
def Answer_SpecificSchedule():
    utteranceParameter = getUtteranceParameter()
    searchName = utteranceParameter['specificschedule']['value']
    print(searchName)

    response = commonResponse
    today = datetime.date.today().isoformat()
    tomorrow = (datetime.date.today()+datetime.timedelta(days=1)).isoformat()
    a_tomorrow = (datetime.date.today()+datetime.timedelta(days=2)).isoformat()
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


    #일정 불러오기
    partschedule = []
    alldayschedule = []

    for i in range(len(calendar_list['items'])):
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
            if todo == searchName or searchName in todo:
                if 'dateTime' in time:
                    T = time['dateTime']
                    if T[8:10] == today[8:10]:
                        partschedule.append("오늘 " + T[11:13] + "시 " + T[14:16] + "분에 " + todo)
                    elif T[8:10] == tomorrow[8:10]:
                        partschedule.append("내일 " + T[11:13] + "시 " + T[14:16] + "분에 " + todo)
                    elif T[8:10] == a_tomorrow[8:10]:
                        partschedule.append("모레 " + T[11:13] + "시 " + T[14:16] + "분에 " + todo)
                    else:
                        Time = T[5:7] + "월 " + T[8:10] + "일 " + T[11:13] + "시 " + T[14:16] + "분"
                        partschedule.append(Time + "에 " + todo)
                        partschedule.sort()
                else:
                    T = str(time.values())
                    if T[8:10] == today[8:10]:
                        alldayschedule.append("오늘 " + todo)
                    elif T[8:10] == tomorrow[8:10]:
                        alldayschedule.append("내일 " + todo)
                    elif T[8:10] == a_tomorrow[8:10]:
                        alldayschedule.append("모레에 " + todo)
                    else:
                        Time = T[19:21] + "월 " + T[22:24] + "일"
                        alldayschedule.append(Time + "에 " + todo)
                        alldayschedule.sort()


    part = '. '.join(partschedule)
    allday = '. '.join(alldayschedule)
    finalresult = part + allday

    print(finalresult)
    response['output']['searchName'] = searchName
    response['output']['existYn'] = 'N'

    if finalresult :
        response['output']['existYn'] = 'Y'
    else: response['output']['existYn'] = 'N'

    response['output']['finalresult'] = finalresult

    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
