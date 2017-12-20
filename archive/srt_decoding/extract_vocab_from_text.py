from __future__ import print_function

import os

path_to_corpus = "/home/dalonlobo/deepspeech_models/srt_decoding"
corpus_file_name = "text_corpus.txt"
actual_path_to_corpus = os.path.join(path_to_corpus, corpus_file_name)

ouput_file_path = "/home/dalonlobo/deepspeech_models/srt_decoding"
output_file_name = "vocabulary.txt"
actual_path_to_output = os.path.join(ouput_file_path, output_file_name)

with open(actual_path_to_corpus, "r") as input_file, \
        open(actual_path_to_output, "a+") as output_file:
    print("Extracting the vocabulary", end="")
    for line in input_file.readlines():
        print(".", end="")
        # Vocab does not consist of special characters
        output_file.write(" ".join(set([word.lower().strip() \
                                        for word in line.split() \
                                        if word.isalpha()]))\
                            + "\n")  # Appending new line
    print("\nExtraction completed")

