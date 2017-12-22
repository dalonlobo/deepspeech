#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 12:42:06 2017

@author: dalonlobo
"""

from __future__ import absolute_import, division, print_function

import subprocess
import sys
import logging
import re

def convert_mp4_to_audio(fpath_in, fpath_out):
    """Convert to wav format with 1 channel and 16Khz freq"""
    cmd = "ffmpeg -i '" + fpath_in + "' -ar 16000 -ac 1 '" + fpath_out + "'"
    logging.debug("Command: " + cmd)
    return cmd

def execute_cmd_on_system(command):
    logging.debug("Executing: " + command[:30] + "...")
    p = subprocess.Popen(command, bufsize=2048, shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         close_fds=(sys.platform != 'win32'))
    output = p.communicate()
    logging.debug("Execution completed: " + command[:30] + "...")
    return output

def pre_process_srt(text):
    # Remove the contents before :
    text = re.sub(r'.*:', '', text)
    # Remove contents inside the paranthesis
    text = re.sub(r"\([^)]*\)", '' , text)
    # Remove special characters
    text = re.sub('[^A-Za-z0-9\s\']+', '', text)
    return text.lower()

def convert_to_ms(st):
    """Converts the subtitle to millisecond"""
    return (st.hours * 60 * 60 * 1000) + (st.minutes * 60 * 1000) +\
                  (st.seconds * 1000) + (st.milliseconds)
                  
                  
                  
    
    
    
    
    