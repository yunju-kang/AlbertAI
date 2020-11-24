#-*-coding:utf-8-*-
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, json
from datetime import datetime
import os
import pickle

from googleapiclient.discovery import build



# 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로
#creds_filename = 'desktop_key.json'
#creds_filename = 'desktop_key.json'
creds_filename = 'C:/Project/gcredential.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']
#flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES, redirect_uri='http://ec2-3-35-46-75.ap-northeast-2.compute.amazonaws.com:5500/')


#flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES, redirect_uri='http://ec2-3-35-46-75.ap-northeast-2.compute.amazonaws.com:5501/')


flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
creds = flow.run_local_server(host='ec2-15-165-243-213.ap-northeast-2.compute.amazonaws.com',port=5501)
#creds = flow.run_local_server(port=0)


with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)


app = Flask(__name__)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501, debug=True)
