#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 09:41:10 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import os
import shutil
import glob
import pysrt
import pandas as pd
import scipy.io.wavfile as wav
import pickle
import logging
import argparse

from timeit import default_timer as timer
from pydub import AudioSegment
from ds_stt import DS
from utils import convert_mp4_to_audio, \
                    execute_cmd_on_system, \
                        pre_process_srt, \
                            convert_to_ms
   
def main(fpath, ds):

    # Buffer size for audio segments in milliseconds
    buffer_in_ms = 200
    
    try:
        # Path to the mp4 file
        mp4_fpath = glob.glob(fpath + "/*.mp4")[0]
        # Path to the srt file
        srt_fpath = glob.glob(fpath + "/*.srt")[0]
        
        # Create temporary directory, to hold the audio chunks
        tmp_dir = os.path.join(fpath, "tmp")
        
        try:
            # Clearing the contents of the directory
            shutil.rmtree(tmp_dir)
        except OSError as e:
            pass
                
        if not os.path.exists(tmp_dir):
            logging.debug("Creating the directory: " + fpath)
            os.makedirs(tmp_dir)
            
        # Path to wav file
        output_wav_path = os.path.join(tmp_dir, "output.wav")
        
        execute_cmd_on_system(\
                convert_mp4_to_audio(mp4_fpath, output_wav_path))
        
        logging.debug("Extracting: " + srt_fpath)
        
        audioSegment = AudioSegment.from_wav(output_wav_path)
        
        # Read the srt
        subtitles = pysrt.open(srt_fpath)  
        ref_text_list = []
        ds_stt_list = []
        for index, subtitle in enumerate(subtitles):
            logging.info('Running {} segment'.format(index))
            start_in_ms = convert_to_ms(subtitle.start)                                
            end_in_ms = convert_to_ms(subtitle.end) 
            
            # pydub segments are in milliseconds
            seg = audioSegment[start_in_ms + buffer_in_ms:end_in_ms + buffer_in_ms]
            
            seg_wav_file_name = os.path.join(tmp_dir, "audio_{}_{}.wav".format(
                    str(start_in_ms), str(end_in_ms)))            
            seg_mp3_file_name = os.path.join(tmp_dir, "audio_{}_{}.mp3".format(
                    str(start_in_ms), str(end_in_ms)))
            # Export as wav for deepspeech recognition
            seg.export(seg_wav_file_name, format="wav")        
            # Export as mp3 for liv.ai recognition
            seg.export(seg_mp3_file_name, format="mp3")
            
            # Deepspeech model processing
            fs, audio = wav.read(seg_wav_file_name)
            # We can assume 16kHz
            audio_length = len(audio) * ( 1 / 16000)        
            logging.info('Running inference.')
            inference_start = timer()
            ds_stt_list.append(ds.stt(audio, fs))
            inference_end = timer() - inference_start
            logging.info('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, 
                                                                    audio_length))
                
            # Process the text to remove (), :, etc
            ref_text_list.append(pre_process_srt(subtitle.text))
                    
        with open(os.path.join(fpath,"text_list.b"), "wb") as f:
            pickle.dump([ref_text_list, ds_stt_list], f)

        logging.debug("All the lists: ")
        logging.debug(ref_text_list)
        logging.debug(ds_stt_list)
        op_df = pd.DataFrame({"Reference": ref_text_list,
                              "Deepspeech hypothesis": ds_stt_list})
    except KeyboardInterrupt as e:
        logging.error("You have exited the program!")
    except Exception as e:
        logging.error(str(e))
    finally:
        try:
            logging.info("Writing output dataframe to:" + os.path.join(fpath,"output_df.b"))
            with open(os.path.join(fpath,"output_df.b"), "wb") as f:
                pickle.dump(op_df, f)
        except Exception as e:
            logging.error(str(e))
        try:
            # Clearing the contents of the directory
            shutil.rmtree(tmp_dir)
        except OSError as e:
            pass
            
if __name__ == "__main__":
    logging.basicConfig(filename="stt_only_ds.logs",
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='Speech to text')
    parser.add_argument('videospath', type=str,  
                        help='Path to the Video files')
    parser.add_argument('--model', type=str,
                        help='Path to the model (protocol buffer binary file)')
    parser.add_argument('--alphabet', type=str,
                        help='Path to the configuration file specifying the alphabet used by the network')
    parser.add_argument('--lm', type=str, 
                        help='Path to the language model binary file')
    parser.add_argument('--trie', type=str, 
                        help='Path to the language model trie file created with native_client/generate_trie')
    args = parser.parse_args()
    logging.info("Program started...")
    # Initialize deepspeech module
    DS = DS(args.model, args.alphabet, args.lm, args.trie)
    # Load the modal
    ds = DS.load_ds_model()
    folders = []
    for root, dirs, files in os.walk(args.videospath):
        folders.append(root)        
    start_time = timer()
    for folder in folders[1:]:
        process_start_time = timer()
        logging.info("Processing the folder: " + str(folder))
        main(folder, ds)
        logging.info('Video %s processed in %0.3f minutes.' \
                     % (folder, ((timer() - process_start_time) / 60)))
    total_time = timer() - start_time
    logging.info('Entire program ran in %0.3f minutes.' % (total_time / 60))
    logging.info("...END...")
    