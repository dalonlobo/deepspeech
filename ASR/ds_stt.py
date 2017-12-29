#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 12:51:52 2017

@author: dalonlobo
"""
from __future__ import absolute_import, division, print_function

import logging

from timeit import default_timer as timer
from deepspeech.model import Model

class DS:
    """ This class will be used to run the Deepspeech model on 
        a segment
    """
    # These constants control the beam search decoder

    # Beam width used in the CTC decoder when building candidate transcriptions
    BEAM_WIDTH = 500
    
    # The alpha hyperparameter of the CTC decoder. Language Model weight
    # LM_WEIGHT = 1.75
    LM_WEIGHT = 2.00
    
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
    
    def __init__(self, model, alphabet, lm=None, trie=None):
        """ Pass the following as parameters:
            model = path to the model 
            alphabet = path to alphabet.txt
            lm = path to language model
            trie = path to trie
        """
    
        self.model = model
        self.alphabet = alphabet
        self.lm = lm
        self.trie = trie
        
    def load_ds_model(self):
        """ Loading the deepspeech module.
            return: deepspeech object
        """
        logging.info('Loading model from file %s' % (self.model))
        model_load_start = timer()
        ds = Model(self.model, self.N_FEATURES, self.N_CONTEXT, 
                   self.alphabet, self.BEAM_WIDTH)
        model_load_end = timer() - model_load_start
        logging.info('Loaded model in %0.3fs.' % (model_load_end))
        
        # Load the lm and trie only if the path is given
        if self.lm and self.trie:
            logging.info('Loading language model from files %s %s' % (self.lm, self.trie))
            lm_load_start = timer()
            ds.enableDecoderWithLM(self.alphabet, self.lm, self.trie, self.LM_WEIGHT,
                                   self.WORD_COUNT_WEIGHT, self.VALID_WORD_COUNT_WEIGHT)
            lm_load_end = timer() - lm_load_start
            logging.info('Loaded language model in %0.3fs.' % (lm_load_end))
            
        return ds
    
