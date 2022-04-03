#!/usr/bin/python3
import math
import os
import pickle
import sys
import getopt
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from weighting import TermFrequency, DocumentFrequency, TfIdfWeight

def create_dictionary(in_dir):
    """
    Reads all files in directory and creates dictionary of terms in each document, posting list of
    documentIds where term is located, and dictionary of term-weight in each document.
    Args:
        in_dir (str): File path of input directory
    Returns:
        term_dict (dict): Dictionary of terms to postings
        weight_dict (dict): Dictionary of documents to normalized weights
    """
    term_dict = {}
    stemmer = PorterStemmer()

    weight_dict = {}
    doc_tf_idf = TfIdfWeight(TermFrequency.LOGARITHM, DocumentFrequency.NO)

    for filename in sorted(os.listdir(in_dir), key=int):
        doc_id = int(filename)
        with open(os.path.join(in_dir, filename), 'r') as f:
            for uncleaned_sentence in sent_tokenize(f.read()):
                # Remove trailing special characters
                sentence = uncleaned_sentence.strip()
                for unstemmed_word in word_tokenize(sentence):
                    # Porter Stemmer + Case-fold
                    word = stemmer.stem(unstemmed_word.lower())

                    # Construct posting 'list' of term and freq of term
                    if word in term_dict:
                        if doc_id in term_dict[word]:
                            term_dict[word][doc_id] += 1
                        else:
                            term_dict[word][doc_id] = 1
                    else:
                        term_dict[word] = {doc_id:1}

                    # Term-Frequency per doc
                    if doc_id in weight_dict:
                        if word in weight_dict[doc_id]:
                            weight_dict[doc_id][word] += 1
                        else:
                            weight_dict[doc_id][word] = 1
                    else:
                        weight_dict[doc_id] = {word:1}

    # Convert term-freq into weight of each term of each doc
    for doc_id, tf_dict in weight_dict.items():
        length_norm = 0

        # Calculate idf
        for token, tf in tf_dict.items():
            wtd = doc_tf_idf.weight(tf)
            
            tf_dict[token] = wtd
            length_norm += wtd * wtd

        # Normalize score
        if length_norm > 0:
            length_norm = math.sqrt(length_norm)

            for token, _ in tf_dict.items():
                tf_dict[token] /= length_norm

    return (term_dict, weight_dict)


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    Builds index from documents stored in the input directory, then output the dictionary file and postings file
    Args:
        in_dir (str): File path of input directory
        out_dict (str): File path of output dictionary
        out_postings (str): File path of output posting
    """
    print('indexing...')
    dictionary_file = {}
    term_dict, weight_dict = create_dictionary(in_dir)
    
    with open(out_postings, 'wb') as posting_f:
        # Write each term's posting list
        for term, posting in term_dict.items():
            written_pos = posting_f.tell()
            written_size = posting_f.write(pickle.dumps(posting))
            dictionary_file[term] = (len(posting), written_pos, written_size)

    with open(out_dict, 'wb') as f:
        # Write term dictonary 
        pickle.dump((dictionary_file, weight_dict), f, pickle.HIGHEST_PROTOCOL)
    

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
