#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 12:24:18 2017

@author: dalonlobo
"""

from __future__ import print_function, division
import pandas as pd
import pickle
import text # WER calulation module from DS repo, it uses Lavenstien distance
import wer
import logging
import argparse
import os

from timeit import default_timer as timer

def convert_to_wer(fpath, model_type):
    foldername = os.path.basename(fpath)
    fpath = os.path.join(fpath, "output_df.b")
    # Read the bianry file with lists
    logging.info("Reading file: " + fpath)
    with open(fpath, "rb") as f:
        text_list = pickle.load(f)

    # Find the shape
    logging.info("Number of audio segments: {}".format(len(text_list[0])))
    
    reference = text_list[0]
    if model_type == "la":
        hypothesis = text_list[2]
    else:
        hypothesis = text_list[1]

    wer_v = []
    wer_wer = []
    for index, ref in enumerate(reference):
        if not ref:
            # Because text.wer throws ZeroDivisionError if ref is null
            wer_v.append([1.0, 1.0])
            continue
        wer_v.append([text.wer(ref, hypothesis[index])])
        wer_wer.append([wer.wer(ref, hypothesis[index])])



    # Push the wer to data frame for easier calculations
    col_name = "WER for " + model_type
    werds_df = pd.DataFrame(wer_v, columns=[col_name])

    #   Remove all the values whose WER > 1 
    werds_df = werds_df[werds_df[col_name] <= 1] 
    
    # Push the wer to data frame for easier calculations
    wer_df = pd.DataFrame(wer_wer, columns=[col_name])
    
    #   Remove all the values whose WER > 1 
    wer_df = wer_df[wer_df[col_name] <= 100]
    
    # ### Lower WER is better
    # Look at these stats
    print(werds_df.describe())
    print(wer_df.describe())
    
    # ### Average of WER
    logging.info("Mean of WER using text.py and wer.py are given below: ")
    logging.info("text.py WER average for " + fpath + ": " + str(werds_df.mean()))
    logging.info("wer.py WER average for " + fpath + ": " + str(wer_df.mean()))
    
    return [foldername, werds_df.mean(), wer_df.mean()]


if __name__ == "__main__":
    logging.basicConfig(filename="wer.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='Calculate the WER using deepspeech wer caculator')
    parser.add_argument('fpath', type=str,  
                        help='Path to the binary files')
    parser.add_argument('model_type', type=str,  
                        help='ds or la (For Deep speech or Liv Ai)')
    args = parser.parse_args()
    logging.info("WER count program started...")
    start_time = timer()
    folders = []
    for root, dirs, files in os.walk(args.fpath):
        folders.append(root)  
    errors = []
    for folder in folders[1:]:
        errors.append(convert_to_wer(folder, args.model_type))
    total_time = timer() - start_time
    logging.info('Entire program ran in %0.3f minutes.' % (total_time / 60))
    for error in errors:
        print(*error, sep=" : ", end="\n")
    logging.info("...END...")
