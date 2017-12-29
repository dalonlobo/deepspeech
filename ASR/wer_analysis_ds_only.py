#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 11:32:39 2017

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
import glob



def main(fpath):
    
    # Path to the mp4 file
    fpath = glob.glob(fpath + "/*_df.b")[0]
    logging.info("Reading file: " + fpath)
    with open(fpath, "rb") as f:
        vdf = pickle.load(f)

    # Find the shape
    logging.info("vdf: Number of audio segments:{}".format(vdf.shape[0]))

    wer_v = []
    wer_wer = []
    for val in vdf.iterrows():
        ref = val[1]["Reference"]
        ds_hyp = val[1]["Deepspeech hypothesis"]
        if not ref:
            # Because text.wer throws ZeroDivisionError if ref is null
            wer_v.append([1.0, 1.0])
            continue
        wer_v.append([text.wer(ref, ds_hyp)])
        wer_wer.append([wer.wer(ref, ds_hyp)])

    # Push the wer to data frame for easier calculations
    werds_df = pd.DataFrame(wer_v, columns=["WER for DS"])

    #   Remove all the values whose WER > 1 
    werds_df = werds_df[werds_df["WER for DS"] <= 1]
    
    # Push the wer to data frame for easier calculations
    wer_df = pd.DataFrame(wer_wer, columns=["WER for DS"])
    
    #   Remove all the values whose WER > 1 
    wer_df = wer_df[wer_df["WER for DS"] <= 100]
    
    # ### Lower WER is better
    # Look at these stats
    werds_df.describe()
    wer_df.describe()
    
    # ### Average of WER
    logging.info("Mean of WER using text.py and wer.py are given below: ")
    logging.info("text.py WER average for " + fpath + ": " + str(werds_df.mean()))
    logging.info("wer.py WER average for " + fpath + ": " + str(wer_df.mean()))


if __name__ == "__main__":
    logging.basicConfig(filename="wer.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='Calculate the WER')
    parser.add_argument('fpath', type=str,  
                        help='Path to the folder with output_df.b files')
    args = parser.parse_args()
    logging.info("WER count program started...")
    folders = []
    for root, dirs, files in os.walk(args.fpath):
        folders.append(root)        
    start_time = timer()
    for folder in folders[1:]:
        process_start_time = timer()
        logging.info("Processing the folder: " + str(folder))
        main(folder)
        logging.info('Video %s processed in %0.3f minutes.' \
                     % (folder, ((timer() - process_start_time) / 60)))
    total_time = timer() - start_time
    logging.info('Entire program ran in %0.3f minutes.' % (total_time / 60))
    logging.info("...END...")
