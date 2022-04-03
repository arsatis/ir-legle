#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import collections
import math

from nltk.tokenize import sent_tokenize, word_tokenize

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

     # delete postings and dictionary file (if it exists)
    if os.path.isfile(out_postings):
        os.remove(out_postings)
    if os.path.isfile(out_dict):
        os.remove(out_dict)

    dir_list = sorted([int(x) for x in os.listdir(in_dir)])
    dir_idx = 0

    dic = {}
    dic_doc_length = {} 

    while dir_idx < len(dir_list):
        doc_id = dir_list[dir_idx]
        with open(in_dir + str(doc_id)) as file:
            doc_dic = collections.defaultdict(int)

            # case-folding
            doc = file.read().lower()

            # tokenization
            tokens = [word_tokenize(d) for d in sent_tokenize(doc)]

            # stemming + appending into dict
            ps = nltk.stem.PorterStemmer()
            for sentence in tokens:
                for i in range(len(sentence)):
                    term = ps.stem(sentence[i])
                    doc_dic[term] += 1
                    if term not in dic.keys():
                        # for each term: {docFreq(df), posting list}
                        # for each posting list: [(doc_id, termFreq(tf)) , ...]
                        dic[term] = [1, [(doc_id, 1)]]
                    else:
                        lst = dic[term][1]
                        last_tuple = lst[-1]
                        if last_tuple[0] == doc_id:
                            lst[-1] = (doc_id, last_tuple[1] + 1)
                        else:
                            lst.append((doc_id, 1))
                            dic[term][0] += 1
                        dic[term][1] = lst

            # compute doc length
            weighted_tfs = []
            for term in doc_dic:
                weighted_tfs.append(1 + math.log10(doc_dic[term]) if doc_dic[term] >= 1 else 0)
            doc_length = sum([x ** 2 for x in weighted_tfs])
            dic_doc_length[doc_id] = doc_length

            dir_idx += 1
            
    dic_terms = list(dic.keys())
    for i in range(len(dic_terms)):
        # dic will now be for each term: {df, [startingPtr, bytesWritten]}
        with open(out_postings, 'a') as write_file_post:
            postingLst = dic[dic_terms[i]][1]
            fileDetails = []
            fileDetails.append(write_file_post.tell())
            bytesWritten = write_file_post.write(str(postingLst))
            fileDetails.append(bytesWritten)
            dic[dic_terms[i]][1] = fileDetails

    # Store N in dic as key 'totalLength'
    dic['totalLength'] = len(dir_list)
    
    # write dic
    with open(out_dict, 'wb') as write_file_dict:
        pickle.dump(dic, write_file_dict)

    # write Reuter's docIDs
    with open("reuterIDs.txt", 'wb') as write_reuter_fileIds:
        pickle.dump(dir_list, write_reuter_fileIds)

    # write dic_doc_length
    with open("doc_length.txt", 'wb') as write_doc_length:
        pickle.dump(dic_doc_length, write_doc_length)

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

# add trailing slash if missing for input directory
if input_directory[:-1] != "/":
    input_directory += "/"

build_index(input_directory, output_file_dictionary, output_file_postings)
