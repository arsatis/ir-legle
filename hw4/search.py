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
        posting_list (list): List of documentId - list of positions pairs
    """
    if term not in dictionary:
        return []

    _, pos, size = dictionary[term]

    postings.seek(pos)
    posting_list = pickle.loads(postings.read(size))
    return posting_list

def intersect_posting_lists(posting_lists):
    """
    Returns the intersection of a list of posting lists.
    """
    # sort posting lists by len, start from smallest posting list
    posting_lists.sort(key=len)

    first_lst = posting_lists[0]
    second_lst = []
    lst_index = 1
    while lst_index < len(posting_lists):
        result_lst = []
        second_lst = posting_lists[lst_index]
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

def boolean_retrieval(dictionary, postings, terms):
    """
    Compute and returns the result of a boolean query
    Args:
        terms   (list[str]): List of terms in a boolean query
    Returns:
        output  (list[int]): List of documentId(s) that satisfies the boolean query
    """
    #! Need to see how dic and posting list looks after implenting positional index + compression (maybe)
    # For now, using get_posting_list()
    # retrieve posting lists of each term: [(docId, tf), ...]
    posting_lists = []
    for i in range(len(terms)):
        posting_lst = get_posting_list(dictionary, postings, terms[i])
        if posting_lst:
            posting_lst = posting_lst[1]
        posting_lists.append(posting_lst)

    print(posting_lists)
    output = intersect_posting_lists(posting_lists)
    return output

def phrasal_retrieval(dictionary, postings, terms):
    """
    Compute and returns the result of a phrasal query
    Args:
        terms   (list[str]): List of terms in a phrasal query
    Returns:
        output  (list[int]): List of documentId(s) that satisfies the phrasal query
    """
    #! Need to see how dic and posting list looks after implenting compression (maybe)
    posting_lists = []

    for phrase in terms:
        posting_list = None
        for word in phrase:
            word_posting_list = get_posting_list(dictionary, postings, word)
            if word_posting_list:
                word_posting_list = word_posting_list[1]

                # if word is first in the phrase -> set it as the main posting list
                # warning: do not check for not posting_list -> will return True if posting_list is an empty list
                if posting_list == None:
                    posting_list = word_posting_list
                    continue

                # else if word is somewhere in the middle of the phrase -> intersect posting lists
                idx_pl = len(posting_list) - 1
                idx_wpl = len(word_posting_list) - 1
                while idx_pl >= 0 and idx_wpl >= 0:
                    # find same documents
                    if posting_list[idx_pl][0] < word_posting_list[idx_wpl][0]:
                        word_posting_list.pop(idx_wpl)
                        idx_wpl -= 1
                    elif posting_list[idx_pl][0] > word_posting_list[idx_wpl][0]:
                        idx_pl -= 1
                    else:
                        _, positions = word_posting_list[idx_wpl]
                        for i in reversed(range(len(positions))):
                            if positions[i] - 1 not in posting_list[idx_pl][1]: # TODO: this line could be optimized (e.g., using two indices instead of not in) if needed
                                positions.pop(i)
                        if not positions:
                            word_posting_list.pop(idx_wpl)
                        idx_pl -= 1
                        idx_wpl -= 1
                while idx_pl < 0 and idx_wpl >= 0:
                    word_posting_list.pop(idx_wpl)
                    idx_wpl -= 1
                    
                # shortcut: positional info is no longer required after this part -> can just keep the positions of the prev word
                posting_list = word_posting_list
        posting_lists.append(posting_list)

    print(posting_lists)
    output = intersect_posting_lists(posting_lists)
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

    print("posting list of 'yong':", get_posting_list(dictionary, postings, 'yong'))

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
        print("type:", query_details.type)
        print("terms:", query_details.terms)

        if query_details.type == "free-text":
            free_text_model = VectorSpaceModel(dictionary, document_weights, postings)
            results = free_text_model.cosine_score(query_details, k=10)
        elif query_details.type == "boolean":
            results = boolean_retrieval(dictionary, postings, query_details.terms)
        elif query_details.type == "phrasal":
            results = phrasal_retrieval(dictionary, postings, query_details.terms)
        else:
            pass
        if results: print(results)

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
