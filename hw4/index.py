#!/usr/bin/python3
import csv
import sys
import getopt
import pickle
import collections
import math
import time

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer

def init_csvreader():
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)

def create_dictionary(in_dir):
    term_dict = {}
    doc_weight = {}
    stemmer = PorterStemmer()

    with open(in_dir, 'r', encoding="utf8") as f:
        # Read rows into a dictionary format
        # Format: document_id, title, content, date_posted, court
        reader = csv.reader(f) 
        
        # Skip header
        next(reader) 
        
        for entry in reader:
            doc_id = int(entry[0])
            content = entry[2]

            word_pos = 0
            for uncleaned_sentence in sent_tokenize(content):
                # Remove trailing special characters + Case-fold
                sentence = uncleaned_sentence.strip().lower()
                doc_dic = collections.defaultdict(int)

                for unstemmed_word in word_tokenize(sentence):
                    # Porter Stemmer
                    term = stemmer.stem(unstemmed_word)
                    
                    doc_dic[term] += 1
                    if term in term_dict.keys():
                        # Increment term
                        freq, posting = term_dict[term]
                        last_id, last_freq = posting[-1]

                        if last_id == doc_id:
                            last_freq.append(word_pos)
                            posting[-1] = (last_id, last_freq)
                        else:
                            posting.append((doc_id, [word_pos]))
                            freq += 1

                        term_dict[term] = (freq, posting)
                    else:
                        # Create tuple of freq and posting of term
                        term_dict[term] = (1, [(doc_id, [word_pos])])
                        
                    word_pos += 1

                # Compute document length
                weighted_tfs = []
                for term in doc_dic:
                    weighted_tfs.append(1 + math.log10(doc_dic[term]) if doc_dic[term] >= 1 else 0)
                doc_length = math.sqrt(sum([x * x for x in weighted_tfs]))
                doc_weight[doc_id] = doc_length

    return (term_dict, doc_weight)

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    Builds index from documents stored in the input directory, then output the dictionary file and postings file
    Args:
        in_dir (str): File path of input directory
        out_dict (str): File path of output dictionary
        out_postings (str): File path of output posting
    """
    print('indexing...')

    init_csvreader()
    
    dictionary_file = {}
    term_dict, doc_weight = create_dictionary(in_dir)
    
    # print(term_dict)
    # print(doc_weight)

    with open(out_postings, 'wb') as posting_f:
        # Write each term's posting list
        for term, posting in term_dict.items():
            written_pos = posting_f.tell()
            written_size = posting_f.write(pickle.dumps(posting))
            dictionary_file[term] = (len(posting), written_pos, written_size)

    with open(out_dict, 'wb') as f:
        # Write term dictonary and document weights
        pickle.dump((dictionary_file, doc_weight), f, pickle.HIGHEST_PROTOCOL)

input_dataset = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input dataset
        input_dataset = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_dataset == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

start = time.time()
build_index(input_dataset, output_file_dictionary, output_file_postings)
end = time.time()
print('Time Taken:', end - start)
