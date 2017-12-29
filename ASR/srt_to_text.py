#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 17:08:24 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import os
import glob
import pysrt
import logging
import argparse

from timeit import default_timer as timer
from utils import pre_process_srt

def process_srt(folder):
    print(folder)
    #srt_fpath = glob.glob(folder + "/*.srt")[0]
    for srt_fpath in glob.glob(folder + "/*.srt"):
        # Read the srt
        subtitles = pysrt.open(srt_fpath)
        op_path = srt_fpath.split("/")[-1] + ".txt"
        logging.info("Writing to: " + op_path)
        with open(op_path, "w+") as f:
            for subtitle in subtitles:
                f.write(pre_process_srt(subtitle.text) + "\n")
        logging.info("Finished writing")
    
if __name__ == "__main__":
    logging.basicConfig(filename="srt_to_text.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='convert srt to text')
    parser.add_argument('srtpath', type=str,  
                        help='Path to srt files')
    
    args = parser.parse_args()
    logging.info("Program started...")

    folders = []
    for root, dirs, files in os.walk(args.srtpath):
        folders.append(root)    
    start_time = timer()
    for folder in folders[1:]:
        process_start_time = timer()
        logging.info("Processing the folder: " + str(folder))
        process_srt(folder)
    if len(folders) == 1:
        process_srt(folders[0])
    logging.info("----Done----")
