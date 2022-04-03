#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import math
import ast
import collections

from nltk.tokenize import word_tokenize

### Global variables
dic = {}
k = 10
N = -1
dic_doc_length = {}
reuters_ids = []

### Functions

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # remove results_file everytime search is executed
    if os.path.isfile(results_file):
        os.remove(results_file)
    
    # load global variables
    global dic, N, dic_doc_length, reuters_ids
    with open(dict_file, 'rb') as file:
        dic = pickle.load(file)
    with open('doc_length.txt', 'rb') as file:
        dic_doc_length = pickle.load(file)
    with open("reuterIDs.txt", 'rb') as file:
        reuters_ids = pickle.load(file)
    N = dic['totalLength']

    # process queries
    ps = nltk.stem.PorterStemmer()
    with open(queries_file) as file:
        for query in file:
            # case-folding
            query = query.lower()

            # tokenization
            tokens = word_tokenize(query)

            # stemming
            for i in range(len(tokens)):
                tokens[i] = ps.stem(tokens[i])
            # print(tokens)

            results = vector_space_ranking(postings_file, tokens)
    
            with open(results_file, 'a') as write_results_file:
                results = " ".join(map(str, results)) 
                write_results_file.write(results + "\n")

    # remove last additional newline
    with open(results_file, 'a') as write_results_file:
        write_results_file.truncate(write_results_file.tell() - len(os.linesep))


def retrieve_posting_list(posting_ptr, size_of_posting, postings_file):
   with open(postings_file) as file:
        file.seek(posting_ptr)
        postings_list = file.read(size_of_posting)
        return ast.literal_eval(postings_list)


def compute_weighted_tf(tf):
    return 1 + math.log10(tf) if tf >= 1 else 0


def compute_tfidf(tokens):
    tfidf = []
    for token, c in tokens.items():
        tf = 1 + math.log10(c) if c >= 1 else 0
        df = dic[token][0] if token in dic else 0
        if df == 0:
            tfidf.append(0)
            continue
        idf = math.log10(N / df)
        tfidf.append(tf * idf)
    return tfidf


def length_normalize(values, doc_id=0):
    output = []
    if doc_id:
        euclid_len = dic_doc_length[doc_id]
    else:
        euclid_len = sum([x ** 2 for x in values])
    if euclid_len == 0:
        return values

    for v in values:
        output.append(v / math.sqrt(euclid_len))
    return output


def cosine_similarity(query_tfidf, docs_tf):
    output = {}
    for key, tf_vals in docs_tf.items():
        score = 0
        for i in range(len(query_tfidf)):
            score += (query_tfidf[i] * tf_vals[i])
        output[key] = score
    return output


def vector_space_ranking(postings_file, tokens):
    tfidf_query = []
    tf_docs = collections.defaultdict(list)

    # convert tokens to counts
    tokens_with_counts = collections.Counter(tokens)

    # represent query as weighted tf-idf vector
    tfidf_query = compute_tfidf(tokens_with_counts)
    # print(tfidf_query)

    for token in tokens_with_counts:
        # represent each doc as weighted tf vector
        if token in dic:
            postings_dict = dict(retrieve_posting_list(dic[token][1][0], dic[token][1][1], postings_file))
            for j in reuters_ids:
                tf_docs[j] += [compute_weighted_tf(postings_dict[j])] if j in postings_dict else [0]
        else:
            for j in reuters_ids:
                tf_docs[j] += [0]

    # length normalize all vectors
    tfidf_query = length_normalize(tfidf_query)
    for i in reuters_ids:
        tf_docs[i] = length_normalize(tf_docs[i], doc_id=i)

    # compute cosine similarity score for query and document vectors
    cs_scores = cosine_similarity(tfidf_query, tf_docs)

    # rank documents w.r.t. query by score
    # return top K documents to user
    # Note: they are already sorted by doc_id next by default due to how retrieve_reuters_ids() work
    cs_topk = collections.Counter(cs_scores).most_common(k)

    # extract docIDs + remove docIDs with score = 0
    cs_topk = [x[0] for x in cs_topk if x[1] > 0]
    #print(cs_topk)
    return cs_topk


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
