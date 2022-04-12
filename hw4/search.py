#!/usr/bin/python3
import pickle
import sys
import getopt

from query import QueryDetails, QueryRefiner
from models import VectorSpaceModel

def get_posting_list(dictionary, postings, term):
    """
    Retrieves posting list of term from posting file
    Args:
        term (str): Target term
    Returns:
        posting_list (list): List of documentId - list of positions pairs
    """
    if term not in dictionary:
        return []

    _, pos, size = dictionary[term]

    postings.seek(pos)
    posting_list = pickle.loads(postings.read(size))
    return posting_list

def boolean_retrieval(terms, dictionary, postings):
    """
    Compute and returns the result of a boolean query
    Args:
        terms   (list[str]): List of terms in a boolean query
    Returns:
        output  (list[int]): List of documentId(s) that satisfies the boolean query
    """
    output = []
    #! Need to see how dic and posting list looks after implenting positional index + compression (maybe)
    # For now, using get_posting_list()
    # retrieve posting lists of each term: [(docId, tf), ...]
    posting_lsts = []
    for i in range(len(terms)):
        posting_lst = get_posting_list(dictionary, postings, terms[i])
        if posting_lst:
            posting_lst = posting_lst[1]
            print(posting_lst)
        posting_lsts.append(posting_lst)

    print(posting_lsts)

    # Optimisation: sort posting lists by len, start from smallest posting list.
    posting_lsts.sort(key=len)

    first_lst = posting_lsts[0]
    second_lst = []
    lst_index = 1
    while lst_index < len(posting_lsts):
        result_lst = []
        second_lst = posting_lsts[lst_index]
        first_lst_ptr = 0
        second_lst_ptr = 0

        while first_lst_ptr < len(first_lst) and second_lst_ptr < len(second_lst):
            if first_lst[first_lst_ptr][0] == second_lst[second_lst_ptr][0]:
                result_lst.append(first_lst[first_lst_ptr])
                first_lst_ptr += 1
                second_lst_ptr += 1
            elif first_lst[first_lst_ptr][0] < second_lst[second_lst_ptr][0]:
                first_lst_ptr += 1
            else:
                second_lst_ptr += 1
        lst_index += 1
        first_lst = result_lst

    # convert tuple to just output the docId
    output = [i[0] for i in first_lst]
    return output

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

    print("posting list of 'yong' : ", get_posting_list(dictionary, postings, 'yong'))

    with open(query_file, 'r') as f:
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

            # TODO: This refiner does nothing at the moment
            refiner = QueryRefiner(query_details)
            refiner.pseudo_relevance_feedback([doc_id for _, doc_id in score_id_pairs])
            refined_query = refiner.get_current_refined()

            score_id_pairs = free_text_model.cosine_score(refined_query)

            debug_lst = list(score_id_pairs)
            print(debug_lst, len(debug_lst))
        elif query_details.type == "boolean":
            results = boolean_retrieval(query_details.terms, dictionary, postings)   
            print(results)    
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
