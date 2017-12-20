#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 10:46:53 2017

@author: dalonlobo
"""

from __future__ import print_function

import os
import glob
import pysrt

# Path to the srt files
srt_files_path = "/home/dalonlobo/deepspeech_models/srt_data"

# Path for the text file
text_file_path = "/home/dalonlobo/deepspeech_models/srt_decoding"
text_file_name = "text_corpus.txt"

# Pattern for matching the srt files
pattern = "*.srt"

# Switch to the srt files directory
os.chdir(srt_files_path)

total_files = len(glob.glob(pattern))

with open(os.path.join(text_file_path, text_file_name), "a+") as text_corpus:
    for srt_file in glob.glob(pattern):
        print("Extracting: ", srt_file)
        subtitles = pysrt.open(srt_file)
        for subs in subtitles:
            text_corpus.write(subs.text.encode('utf-8').strip() + "\n")
        print("Done extracting", srt_file)
        
print("Total files extracted: ", total_files)


    