#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:00:09 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function


import pandas as pd
import logging
import glob
import os
import argparse

if __name__ == "__main__":
    logging.basicConfig(filename="common_speech_text_cleanup.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='common speech text cleanup')
    parser.add_argument('fpath', type=str,  
                        help='Path to the folder which contains input files')
    parser.add_argument('op_path', type=str,  
                        help='Path to store the output files')
    args = parser.parse_args()
    folder = args.fpath
    op_path = args.op_path
    if not os.path.exists(op_path):
        logging.debug("Creating the directory: " + op_path)
        os.makedirs(op_path)
    
    for fpath in glob.glob(folder + os.sep + "*.csv"):
        logging.debug("Reading file: " + fpath)
        df = pd.read_csv(fpath)
        with open(os.path.join(op_path, os.path.basename(fpath) + ".txt"), "w+") as f:
            for trans in df.transcript:
                f.write(str(trans) + "\n")
