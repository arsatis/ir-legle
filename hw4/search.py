#!/usr/bin/python3
import pickle
import sys
import getopt

from query import QueryDetails
from models import VectorSpaceModel

def get_posting_list(dictionary, postings, term):
    """
    Retrieves posting list of term from posting file
    Args:
        term (str): Target term
    Returns:
        posting_list (list): List of documentId-frequency pairs
    """
    if term not in dictionary:
        return []

    _, pos, size = dictionary[term]

    postings.seek(pos)
    posting_list = pickle.loads(postings.read(size))
    
    return posting_list

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, query_file, results_file):
    """
    Using the given dictionary file and postings file, perform searching on the given queries file
    and output the results to a file
    Args:
        dict_file     (str): File path of input dictionary file
        postings_file (str): File path of input posting file
        queries_file  (str): File path of input query file
        results_file  (str): File path of output result file
    """
    print('running search on the queries...')

    # TEMPORARY READ DICT AND POSTING
    with open(dict_file, 'rb') as f:
        dictionary, document_weights = pickle.load(f)

    postings = open(postings_file, 'rb')

    print(get_posting_list(dictionary, postings, 'yong'))

    with open(query_file) as f:
        count = 0
        lst_of_relevant_docs = []

        for line in f:
            if count == 0: # first line
                query = line
            else:
                lst_of_relevant_docs.append(int(line))
            count += 1

        query_details = QueryDetails(query, lst_of_relevant_docs)
        print("type: ", query_details.type)
        print("terms: ", query_details.terms)

        if query_details.type == "free-text":
            # vector space ranking for free text queries
            free_text_model = VectorSpaceModel(dictionary, document_weights, postings)
            score_id_pairs = free_text_model.cosine_score(query_details, k=10)
            print(list(score_id_pairs))
        else:
            pass

dictionary_file = postings_file = query_file = output_file_of_results = None

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
        query_file = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or query_file == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, query_file, file_of_output)
