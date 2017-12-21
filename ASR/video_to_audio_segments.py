#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 09:41:10 2017

@author: dalonlobo
"""
from __future__ import print_function

import subprocess
import sys
import os
import os.path as ospath
import shutil
import glob
import pysrt
import pandas as pd
import scipy.io.wavfile as wav
import text

from timeit import default_timer as timer
from deepspeech.model import Model
from pydub import AudioSegment
from pydub.effects import normalize


def convert_mp4_to_audio(fpath_in, fpath_out):
    """Convert to wav format with 1 channel and 16Khz freq"""
    cmd = "ffmpeg -i '" + fpath_in + "' -ar 16000 -ac 1 '" + fpath_out + "'"
    return cmd

def execute_cmd_on_system(command):
    p = subprocess.Popen(command, bufsize=2048, shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         close_fds=(sys.platform != 'win32'))
    output = p.communicate()
    print("Executed : " + command)
    
def main(fpath):
    
    # Buffer size for audio segments in milliseconds
    buffer_in_ms = 200
    
    MSL = 500 # minimum silence length in ms
    
    # These constants control the beam search decoder

    # Beam width used in the CTC decoder when building candidate transcriptions
    BEAM_WIDTH = 500
    
    # The alpha hyperparameter of the CTC decoder. Language Model weight
    # LM_WEIGHT = 1.75
    LM_WEIGHT = 1.75
    
    # The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
    WORD_COUNT_WEIGHT = 1.00
    
    # Valid word insertion weight. This is used to lessen the word insertion penalty
    # when the inserted word is part of the vocabulary
    VALID_WORD_COUNT_WEIGHT = 1.00
    
    
    # These constants are tied to the shape of the graph used (changing them changes
    # the geometry of the first layer), so make sure you use the same constants that
    # were used during training
    
    # Number of MFCC features to use
    N_FEATURES = 26
    
    # Size of the context window used for producing timesteps in the input vector
    N_CONTEXT = 9
    
    
#   Use the following for defaults
    model = "/home/dalonlobo/deepspeech_models/models/output_graph.pb"
    alphabet = "/home/dalonlobo/deepspeech_models/models/alphabet.txt"
    lm = "/home/dalonlobo/deepspeech_models/models/lm.binary"
    trie = "/home/dalonlobo/deepspeech_models/models/trie"
    
#    Read the videos from the folder
#    for root, subdirs, files in os.walk(walk_dir):
    
    # Path to the mp4 file
    mp4_fpath = glob.glob(fpath + "/*.mp4")[0]
    # Path to the srt file
    srt_fpath = glob.glob(fpath + "/*.srt")[0]
    
    # Create temporary directory, to hold the audio chunks
    tmp_dir = os.path.join(os.path.dirname(fpath), "tmp")
    
    try:
        # Clearing the contents of the directory
        shutil.rmtree(tmp_dir)
    except OSError as e:
        print(str(e))
            
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        
    # Path to wav file
    output_wav_path = ospath.join(tmp_dir, "output.wav")
    
#    # Path to mp3 file
#    output_mp3_path = ospath.join(ospath.split(ospath.abspath(fpath))[0],\
#                                  "tmp", "output.mp3")
    
    execute_cmd_on_system(\
            convert_mp4_to_audio(mp4_fpath, output_wav_path))
    
    print("Extracting: ", srt_fpath)
    subtitles = pysrt.open(srt_fpath)
    
    
    audioSegment = AudioSegment.from_wav(output_wav_path)
    
    # Loading the deepspeech module
    print('Loading model from file %s' % (model), file=sys.stderr)
    model_load_start = timer()
    ds = Model(model, N_FEATURES, N_CONTEXT, 
               alphabet, BEAM_WIDTH)
    model_load_end = timer() - model_load_start
    print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)

    if lm and trie:
        print('Loading language model from files %s %s' % (lm, trie), 
                file=sys.stderr)
        lm_load_start = timer()
        ds.enableDecoderWithLM(alphabet, lm, trie, LM_WEIGHT,
                               WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)
        lm_load_end = timer() - lm_load_start
        print('Loaded language model in %0.3fs.' % (lm_load_end), 
              file=sys.stderr)
    
    for subtitle in subtitles:
        start_in_ms = (subtitle.start.hours * 60 * 60 * 1000) +\
                        (subtitle.start.minutes * 60 * 1000) +\
                          (subtitle.start.seconds * 1000) +\
                            (subtitle.start.milliseconds)
                            
        end_in_ms = (subtitle.end.hours * 60 * 60 * 1000) +\
                        (subtitle.end.minutes * 60 * 1000) +\
                          (subtitle.end.seconds * 1000) +\
                            (subtitle.end.milliseconds)
        
        # pydub segments are in milliseconds
        seg = audioSegment[start_in_ms + buffer_in_ms:end_in_ms + buffer_in_ms]
        # Export as wav for deepspeech recognition
        seg.export(ospath.join(tmp_dir, "audio_{}_{}.wav".format(
                str(start_in_ms), str(end_in_ms))), format="wav")
    
        # Export as mp3 for liv.ai recognition
        seg.export(ospath.join(tmp_dir, "audio_{}_{}.mp3".format(
                str(start_in_ms), str(end_in_ms))), format="mp3")
        
        seg_file_name = ospath.join(tmp_dir, "audio_{}_{}.wav".format(
                str(start_in_ms), str(end_in_ms)))
#        print(seg_file_name)
        
        fs, audio = wav.read(seg_file_name)
        # We can assume 16kHz
        audio_length = len(audio) * ( 1 / 16000)
    
        print('Running inference.', file=sys.stderr)
        inference_start = timer()
        deepspeech_stt = ds.stt(audio, fs)
        print(deepspeech_stt)
        inference_end = timer() - inference_start
        print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, 
                                                                audio_length), 
                file=sys.stderr)
        
        reference = seg.text
        print("WER of deepspeech model:")
        print(text.wer(seg.text, deepspeech_stt))
        
if __name__ == "__main__":
    fpath = "/home/dalonlobo/deepspeech_models/deepspeech/ASR/youtube-dl-videos/DWtnKRL30jo/"
    main(fpath)
    
    
    
    
    
    