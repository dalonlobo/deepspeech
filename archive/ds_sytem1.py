#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:48:01 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import os
import os.path as ospath
import sys
import subprocess
import argparse
import wer
import pickle
import shutil
import pandas as pd
import scipy.io.wavfile as wav

from timeit import default_timer as timer
from deepspeech.model import Model
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence

class AudioProcessing():
    
    DEBUG = False # set to true for verbose 
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
    
    def __init__(self, args):
        self.fpath = args.fpath # Input video file path
        self.args = args
     
    def convert_mp4_to_wav(self, fpath_in, fpath_out):
        """Convert to wav format with 1 channel and 16Khz freq"""
        cmd = "ffmpeg -i '" + fpath_in + "' -ar 16000 -ac 1 '" + fpath_out + "'"
        return cmd
    
    def execute_cmd_on_system(self, command):
        p = subprocess.Popen(command, bufsize=2048, shell=True, 
                             stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             close_fds=(sys.platform != 'win32'))
        output = p.communicate()
        print("Executed : " + command)
        if self.DEBUG:
            print(output)
        
    def process_wav(self):      
        # Create temporary directory, to hold the audio chunks
        tmp_dir = os.path.join(os.path.dirname(self.fpath), "tmp")
        
        try:
            # Clearing the contents of the directory
            shutil.rmtree(tmp_dir)
        except OSError as e:
            print(e.message)
        
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        
        # Convert mp4 to wav
        output_wav_path = ospath.join(ospath.split(ospath.abspath(self.fpath))[0],\
                                      "tmp", "output.wav")
        self.execute_cmd_on_system(\
                self.convert_mp4_to_wav(self.fpath, output_wav_path))
        # Segmenting the audio
        input_audio = AudioSegment.from_file(output_wav_path, format="wav")
        # Normalizing the audio file
        full_audio_wav = normalize(input_audio)
        print("Length of the entire audio: ", len(full_audio_wav))
        
        # Calculating the silence threshold
        loudness_ms_list = []
        for ms_chunk in full_audio_wav:
            loudness_ms_list.append(round(ms_chunk.dBFS))
            
        # Dump into the pickle for debugging
        with open("pickle_dump.b", "wb") as p:
            pickle.dump(pd.DataFrame(loudness_ms_list), p)
        
        # st = silence threshold
        st = pd.DataFrame(loudness_ms_list)
        # Remove the inf
        st = st[st[0] != float("-inf")]
        st = round(st.mean()[0], 2)
        
        print("Set the silence threshold to: ", st)
        st = st if st < -16 else -16 # Because -16db is default
        chunks = split_on_silence(
            full_audio_wav,
        
            # split on silences longer than 1000ms (1 sec)
            min_silence_len=self.MSL,
        
            # anything under -16 dBFS is considered silence
            silence_thresh=st,  # hardcoded for now
        
            # keep 250 ms of leading/trailing silence
            keep_silence=200,
            
        )
        
#        for i, chunk in enumerate(chunks):
#            chunk_file_name = tmp_dir + "/chunk{0}.wav".format(i)
#            chunk.export(chunk_file_name, format="wav")      

        # Loading the deepspeech module
        print('Loading model from file %s' % (self.args.model), file=sys.stderr)
        model_load_start = timer()
        ds = Model(self.args.model, self.N_FEATURES, self.N_CONTEXT, 
                   self.args.alphabet, self.BEAM_WIDTH)
        model_load_end = timer() - model_load_start
        print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)
    
        if self.args.lm and self.args.trie:
            print('Loading language model from files %s %s' % (self.args.lm, 
                                                               self.args.trie), 
                    file=sys.stderr)
            lm_load_start = timer()
            ds.enableDecoderWithLM(self.args.alphabet, self.args.lm, 
                                   self.args.trie, self.LM_WEIGHT,
                                   self.WORD_COUNT_WEIGHT, 
                                   self.VALID_WORD_COUNT_WEIGHT)
            lm_load_end = timer() - lm_load_start
            print('Loaded language model in %0.3fs.' % (lm_load_end), 
                  file=sys.stderr)
            
        output_text_file = self.args.tspath  
        with open(output_text_file, "w+") as output_text:
            for i, chunk in enumerate(chunks):
                chunk_file_name = tmp_dir + "/chunk{0}.wav".format(i)
                chunk.export(chunk_file_name, format="wav")
                fs, audio = wav.read(chunk_file_name)
                # We can assume 16kHz
                audio_length = len(audio) * ( 1 / 16000)
            
                print('Running inference.', file=sys.stderr)
                inference_start = timer()
                model_stt = ds.stt(audio, fs) + " "
                print(model_stt)
                output_text.write(model_stt)
                inference_end = timer() - inference_start
                print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, 
                                                                        audio_length), 
                        file=sys.stderr)
        print("Processing done")
        
    def get_wer(self):
        r = file(self.args.refpath).read().split()
        h = file(self.args.tspath).read().split()
        wer.wer(r, h)   
        
def main():
        # Use the following for defaults
    #  model       /home/dalonlobo/deepspeech_models/models/output_graph.pb
    #  audio       /home/dalonlobo/deepspeech_models/models/2830-3980-0043.wav 
    #  alphabet    /home/dalonlobo/deepspeech_models/models/alphabet.txt
    #  lm          /home/dalonlobo/deepspeech_models/models/lm.binary
    #  trie        /home/dalonlobo/deepspeech_models/models/trie
    
    # python audio_processing.py --fpath v2.mp4 
    
    parser = argparse.ArgumentParser(description="Preprocessing the audio")
    parser.add_argument("--fpath", type=str,
                        help="Enter the file path to the video mp4 file")
    parser.add_argument('--model', type=str,  nargs='?',
                        default='/home/dalonlobo/deepspeech_models/models/output_graph.pb',
                        help='Path to the model (protocol buffer binary file)')
    parser.add_argument('--audio', type=str, nargs='?',
                        default='/home/dalonlobo/deepspeech_models/models/2830-3980-0043.wav',
                        help='Path to the audio file to run (WAV format)')
    parser.add_argument('--alphabet', type=str,  nargs='?',
                        default='/home/dalonlobo/deepspeech_models/models/alphabet.txt',
                        help='Path to the configuration file specifying the alphabet used by the network')
    parser.add_argument('--lm', type=str, nargs='?',
                        default='/home/dalonlobo/deepspeech_models/models/lm.binary',
                        help='Path to the language model binary file')
    parser.add_argument('--trie', type=str, nargs='?',
                        default='/home/dalonlobo/deepspeech_models/models/trie',
                        help='Path to the language model trie file created with native_client/generate_trie')
    parser.add_argument('--tspath', type=str, nargs='?',
                        default='ds_transcription.txt',
                        help='Path where the output has to be saved')   
    parser.add_argument('--refpath', type=str, nargs='?',
                        default='reference.txt',
                        help='Path to reference.txt for wer calculation')       
    args = parser.parse_args()

    audio = AudioProcessing(args)
    audio.process_wav()
    audio.get_wer()
        
if __name__ == "__main__":
    main()  
            
            
            
            
            
            
            
            
            