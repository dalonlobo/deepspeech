#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:00:09 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import logging
import glob
import os
import argparse
import re

if __name__ == "__main__":
    logging.basicConfig(filename="create_vocab.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='Convert to vocabulary')
    parser.add_argument('fpath', type=str,  
                        help='Path to the folder which contains text files')
    parser.add_argument('op_path', type=str,  
                        help='Path to store the output files')
    args = parser.parse_args()
    folder = args.fpath
    op_path = args.op_path
    print(folder)
    tokens = []
    for fpath in glob.glob(folder + os.sep + "*.txt"):
        print(fpath)
        logging.debug("Reading file: " + fpath)
        with open(fpath, "r") as f, open(op_path, "w+") as op:
            for line in f:
                # # Remove the digits
                line = re.sub('[^A-Za-z\s\']+', '', line)
                op.write(line + "\n")

            
            
            
