#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 11:22:53 2017

@author: dalonlobo
"""

import pickle
import pandas as pd

with open("pickle_dump.b", "rb") as f:
    st = pickle.load(f)
    
df = st[st[0] != float("-inf")]

df.describe()
    
df.hist()