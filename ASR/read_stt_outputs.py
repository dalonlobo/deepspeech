#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 15:14:15 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    with open("output_df.b", "rb") as f:
        df = pickle.load(f)
    
    print("Shape of the df: ", df.shape)
    
    print("Distribution:")
    print(df.describe())
    
#   Values greater than 1
    greater_than_one_df = df[(df["Deepspeech WER"] > 1) | (df["Livai WER"] > 1)]
    
    greater_than_one_df.head()
    
#   Remove all the values whose WER > 1 
    df = df[df["Deepspeech WER"] <= 1]
    df = df[df["Livai WER"] <= 1]
    
    print("Distribution:")
    print(df.describe())
    
    df.hist()
    
    print("Number of worst case predictions:")
    print("For Deepspeech", df[df["Deepspeech WER"] == 1].count()[0])
    print("For Livai", df[df["Livai WER"] == 1].count()[0])
    
if __name__ == "__main__":
    main()