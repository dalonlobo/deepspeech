#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 13:56:08 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import time
import logging
import requests
import json

from requests.exceptions import ConnectionError

class LIVAI():
    """
    This class deals with everything related to liv ai
    """
    
    #    Liv.ai authentication token and user
    TOKEN = 'f6406f7a3ecba98a61db03be55b408f957728d85' 
    USER = '14038'
    
    def __init__(self):
        pass
        
    def upload(self, mp3_file_name):
        logging.info("Uploading to liv ai")
        headers = {'Authorization' : 'Token ' + self.TOKEN}
        data = {'user' : self.USER , 'language' : 'EN', 'transcribe' : 1}
        files = {'audio_file' : open(mp3_file_name,'rb')}
        url = 'https://dev.liv.ai/liv_speech_api/recordings/'
        response = requests.post(url, headers = headers, data = data, files = files)
        logging.debug(str(json.dumps(response.json(), indent=4, sort_keys=True)))
        return response.json()['app_session_id']
    
    def upload_status(self, session_id):
        # Check the status            
        headers = {'Authorization' : 'Token ' + self.TOKEN}
        params = {'app_session_id' : session_id}
        url = 'https://dev.liv.ai/liv_speech_api/session/status/'
        status = requests.get(url, headers = headers, params = params)
        logging.debug(str(json.dumps(status.json(), indent=4, sort_keys=True)))
        return status.json()["upload_status"], status.json()["transcribed_status"]
    
    def get_stt(self, session_ids):
        liv_stt = []
        for session_id in session_ids:
            try:
                if session_id == '':
                    liv_stt.append('')
                    continue
                upload_status, transcribed_status = self.upload_status(session_id)
                # Following are the upload status
                # https://liv.ai/api/long_audio/#get-session-status
                while upload_status in ["0","10", "11", "20"]:
                    time.sleep(1) # Liv ai is rate limited 1call per second
                    upload_status, transcribed_status = self.upload_status(session_id)      
                
                if int(upload_status) < 0:
                    logging.error("Something went wrong in livai, session id & status: ",\
                                  session_id, upload_status)
                else:            
                    # Wait until the audio is processed
                    while not transcribed_status:
                        time.sleep(1)  # Respect the rate limit
                        upload_status, transcribed_status = self.upload_status(session_id)
                    time.sleep(1)
                    logging.debug("Obtaining the transcription for :" + session_id)
                    # Get the transcription
                    headers = {'Authorization' : 'Token ' + self.TOKEN}
                    params = {'app_session_id' : session_id}
                    url = 'https://dev.liv.ai/liv_speech_api/session/transcriptions/'
                    try:
                        response = requests.get(url, headers = headers, params = params)
                        logging.debug(str(json.dumps(response.json(), indent=4, sort_keys=True)))
                        liv_stt.append(str(response.json()["transcriptions"][0]["utf_text"]\
                                                .encode('utf-8')))
                    except ConnectionError as e:
                        logging.error(str(e))
                        logging.error("New connection error")
                        liv_stt.append('')
            except Exception as e:
                logging.error(str(e))
                liv_stt.append('')

            time.sleep(1) # Respect rate limit
        return liv_stt
                
                