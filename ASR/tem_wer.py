#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 11:28:47 2018

@author: dalonlobo
"""
import pickle
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

def convert_to_wer(error):

    reference = error[1]
    hypothesis = error[2]

    wer_v = []
    wer_wer = []
    for index, ref in enumerate(reference):
        try:
            wer_v.append([text.wer(ref, hypothesis[index])])
        except ZeroDivisionError:
            wer_v.append([1.0])
        try:
            wer_wer.append([wer.wer(ref, hypothesis[index])])
        except ZeroDivisionError:
            wer_wer.append([100])


    # Push the wer to data frame for easier calculations
    col_name = "WER for DS"
    werds_df = pd.DataFrame(wer_v, columns=[col_name])

    #   Remove all the values whose WER > 1 
    werds_df = werds_df[werds_df[col_name] <= 1] 
    
    # Push the wer to data frame for easier calculations
    wer_df = pd.DataFrame(wer_wer, columns=[col_name])
    
    #   Remove all the values whose WER > 1 
    wer_df = wer_df[wer_df[col_name] <= 100]
    
    # ### Lower WER is better
    # Look at these stats

    
    print("{} : {} : {}".format(error[0], werds_df["WER for DS"].mean(), 
          wer_df["WER for DS"].mean()))



if __name__ == "__main__":
    logging.basicConfig(filename="tem.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    with open("long_vid.b", "rb") as f:
        errors = pickle.load(f)
    
    fpath = "longvideos_full_trans"
    if not os.path.exists(fpath):
        logging.debug("Creating the directory: " + fpath)
        os.makedirs(fpath)
    
    for error in errors:
        path = os.path.join(fpath, error[0])
        if not os.path.exists(path):
            logging.debug("Creating the directory: " + path)
            os.makedirs(path)
        with open(os.path.join(path, error[0] + "_ref.txt"), "w") as f:
            for line in error[1]:
                f.write(line + " ")
        with open(os.path.join(path, error[0] + "_hyp.txt"), "w") as f:
            for line in error[2]:
                f.write(line + " ")
#        convert_to_wer(error)


