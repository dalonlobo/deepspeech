#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:44:12 2017

@author: dalonlobo
"""

import subprocess

ffmpeg -i part2_2.mp4 -ar 16000 -ac 1 part2_2.wav

input_mp4_path = ""
wav_path = ""

subprocess.call(['ffmpeg', '-i', input_mp4_path, '-ar', '16000',
                   '-ar', '1', wav_path])