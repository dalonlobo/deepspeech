#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 09:19:29 2017

@author: dalonlobo
"""

import requests
import json
import time

# Authentication token
TOKEN = 'f6406f7a3ecba98a61db03be55b408f957728d85' 

# Long audio
headers = {'Authorization' : 'Token ' + TOKEN}
data = {'user' : '14038' ,'language' : 'EN','transcribe' : 1}
files = {'audio_file' : open('git.mp3','rb')}
url = 'https://dev.liv.ai/liv_speech_api/recordings/'
res1 = requests.post(url, headers = headers, data = data, files = files)
session_id = res1.json()['app_session_id']
print(json.dumps(res1.json(), indent=4, sort_keys=True))

# Check the status

headers = {'Authorization' : 'Token ' + TOKEN}
params = {'app_session_id' : session_id}
url = 'https://dev.liv.ai/liv_speech_api/session/status/'
res2 = requests.get(url, headers = headers, params = params)
print(json.dumps(res2.json(), indent=4, sort_keys=True))

# Get the transcription
headers = {'Authorization' : 'Token ' + TOKEN}
params = {'app_session_id' : session_id}
url = 'https://dev.liv.ai/liv_speech_api/session/transcriptions/'
res3 = requests.get(url, headers = headers, params = params)
print(json.dumps(res3.json(), indent=4, sort_keys=True))

with open("livai_git.txt", "w+") as f:
    f.write(res3.json()["transcriptions"][0]["utf_text"])


# These mp3 files are test files provided by deepspeech

# #Filename #OutputFromDeepspeech               #OutputFromLivai
#   1.mp3   "experience proves this"            "experience"
#   2.mp3   "why should one halt on the way"    "why should one hold on the way"
#   3.mp3   "your power is sufficient i said"   "you flower is a fresher i"



















