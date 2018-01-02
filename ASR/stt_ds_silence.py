#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 16:27:36 2018

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
import sys

from timeit import default_timer as timer
from ds_stt import DS
from utils import convert_mp4_to_audio, \
                    execute_cmd_on_system, \
                        pre_process_srt, \
                            convert_to_ms
                            
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence
   
def main(fpath, ds):
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
        
        audioSegment = AudioSegment.from_wav(output_wav_path)
        
        # Calculating the silence threshold
        # Normalizing the audio file
        full_audio_wav = normalize(audioSegment)
        loudness_ms_list = []
        for ms_chunk in full_audio_wav:
            loudness_ms_list.append(round(ms_chunk.dBFS))
        logging.debug("loudness_ms_list")
        logging.debug(loudness_ms_list)
        # st = silence threshold
        df = pd.DataFrame(loudness_ms_list)
        df[0] = df[df[0] != float("-inf")]
        st = df[0].mean()
        st = st if st < -16 else -16 # Because -16db is default
        logging.info("Set the silence threshold to: " + str(st))
        MSL = 500 # minimum silence length in ms
        chunks = split_on_silence(
            full_audio_wav,
        
            # split on silences longer than 1000ms (1 sec)
            min_silence_len=MSL,
        
            # anything under -16 dBFS is considered silence
            silence_thresh=st,  # hardcoded for now
        
            # keep 250 ms of leading/trailing silence
            keep_silence=200,
            
        )

        ds_stt_list = []
        for index, chunk in enumerate(chunks):
#            if index < 3:
#                break
            chunk_file_name = os.path.join(tmp_dir, "chunk{0}.wav".format(index))
            chunk.export(chunk_file_name, format="wav")
            fs, audio = wav.read(chunk_file_name)
            # We can assume 16kHz
            audio_length = len(audio) * ( 1 / 16000)
            
            logging.info('Running segment number {}'.format(index))
            logging.info('Running inference.')
            inference_start = timer()
            ds_stt_list.append(ds.stt(audio, fs))
            inference_end = timer() - inference_start
            logging.info('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, 
                                                                    audio_length))
                
        logging.info("Writing the output list as binary")          
        with open(os.path.join(fpath,"text_list.b"), "wb") as f:
            pickle.dump([ds_stt_list], f)
            
        # Writing the deepspeech output to text file
        logging.info("Writing the entire ds output to file")
        with open(os.path.join(os.path.dirname(mp4_fpath), 
                               os.path.basename(mp4_fpath) + "_hyp.txt"), "w") as f: 
            for index, val in enumerate(ds_stt_list):
                f.write(val + " ")

        # srt processing
        # Read the srt
        logging.debug("Extracting: " + srt_fpath)
        subtitles = pysrt.open(srt_fpath)
        with open(os.path.join(os.path.dirname(srt_fpath), 
                               os.path.basename(srt_fpath) + "_ref.txt"), "w") as f: 
            for index, subtitle in enumerate(subtitles):
                f.write(pre_process_srt(subtitle.text) + " ")

        logging.debug("All the lists: ")
        logging.debug(ds_stt_list)
        op_df = pd.DataFrame({"Deepspeech hypothesis": ds_stt_list})
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
#        try:
#            # Clearing the contents of the directory
#            shutil.rmtree(tmp_dir)
#        except OSError as e:
#            pass
            
if __name__ == "__main__":
    logs_path = os.path.basename(__file__) + ".logs"
    logging.basicConfig(filename=logs_path,
        filemode='a',
        format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    print("Logs are saved to: ", logs_path, file=sys.stderr)
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
    # Load the model
    ds = DS.load_ds_model()
    folders = []
    for root, dirs, files in os.walk(args.videospath):
        folders.append(root)        
    start_time = timer()
    print(folders[1:], file=sys.stderr)
    for folder in folders[1:]:
        process_start_time = timer()
        logging.info("Processing the folder: " + str(folder))
        main(folder, ds)
        logging.info('Video %s processed in %0.3f minutes.' \
                     % (folder, ((timer() - process_start_time) / 60)))
    total_time = timer() - start_time
    logging.info('Entire program ran in %0.3f minutes.' % (total_time / 60))
    print("...End...", file=sys.stderr)
    logging.info("...END...")
 