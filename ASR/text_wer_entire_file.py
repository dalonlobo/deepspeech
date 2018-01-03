#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 18:01:10 2018

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function
import text
import sys
import os

if __name__ == "__main__":
    folders = []
    fpath = os.path.abspath("temp_playlist")
    for root, dirs, files in os.walk(fpath):
        folders.append(root) 
    print(folders[1:], file=sys.stderr)
    for folder in folders[1:]:
        ref_fpath = glob.glob(os.path.join(fpath,folder) + "/*_ref.txt")[0]
        hyp_fpath = glob.glob(os.path.join(fpath,folder) + "/*_hyp.txt")[0]
        print(ref_path, hyp_path)
        with open(ref_fpath) as f1, open(ref_fpath) as f2:
            text.wer(f1.read(), f2.read())
