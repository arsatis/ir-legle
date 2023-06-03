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
        term          (str): Target term
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
    NOTE: This method is deprecated.
    Returns the intersection of a list of posting lists along with the total term frequency.
    Args:
        posting_lists (list): List of posting lists along with the total term frequency
    Returns:
        output        (list): Intersection of the posting lists
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
    output = [(i[0], len(i[1])) for i in first_lst]
    return output

def rank_docs(docs):
    """
    NOTE: This method is deprecated.
    Ranks the documents in descending order based on their weight.
    Args:
        docs   (list): List of documents along with their weights (i.e., counts)
    Returns:
        output (list): List of documents, sorted in descending order based on their weight
    """
    docs.sort(key=lambda x: x[1], reverse=True)
    return docs

def boolean_phrasal_retrieval(dictionary, postings, terms):
    """
    NOTE: This method is deprecated.
    Compute and returns the result of a boolean/phrasal query.
    Args:
        terms   (list): List of terms in a boolean/phrasal query
    Returns:
        output  (list): List of documentId(s) that satisfies the boolean/phrasal query
    """
    posting_lists = []

    for phrase in terms:
        # Boolean query
        if isinstance(phrase, str):
            posting_list = get_posting_list(dictionary, postings, phrase)
            if posting_list:
                posting_list = posting_list[1]

        # Phrasal query
        else:
            posting_list = None
            for word in phrase:
                word_posting_list = get_posting_list(dictionary, postings, word)
                if word_posting_list:
                    word_posting_list = word_posting_list[1]

                    # If word is first in the phrase -> set it as the main posting list
                    # Warning: do not check for not posting_list -> will return True if posting_list is an empty list
                    if posting_list == None:
                        posting_list = word_posting_list
                        continue

                    # Else if word is somewhere in the middle of the phrase -> intersect posting lists
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
                                if positions[i] - 1 not in posting_list[idx_pl][1]:
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

    output = rank_docs(intersect_posting_lists(posting_lists))
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

    with open(dict_file, 'rb') as f:
        dictionary, document_weights = pickle.load(f)

    postings = open(postings_file, 'rb')

    with open(query_file, 'r') as f, open(results_file, 'w') as r_file:
        count = 0
        lst_of_relevant_docs = []

        for line in f:
            if count == 0: # first line
                query = line
            else:
                lst_of_relevant_docs.append(int(line))
            count += 1

        query_details = QueryDetails(query, lst_of_relevant_docs)

        if query_details.type == "invalid":
            print("Invalid query! Result will be empty")
            write_result(r_file, [])
            return

        if query_details.type != "free-text": # Boolean / boolean with phrasal
            query_details.to_free_text()

        # Query Expansion
        refiner = QueryRefiner(query_details)
        refiner.query_expansion(6)
        refined_query = refiner.get_current_refined()

        # Vector space ranking for free text queries
        free_text_model = VectorSpaceModel(dictionary, document_weights, postings)
        score_id_pairs = free_text_model.cosine_score(refined_query)

        results = [(id, score) for score, id in score_id_pairs]

        # Score based on zone
        title_a = 0.2
        content_a = 1 - title_a
        new_results = {}
        for id, score in results:
            zone = id[-1]
            clean_id = id[:-2]
            if clean_id not in new_results:
                if zone == "c": # Content
                    new_results[clean_id] = content_a * score
                else: # Title
                    new_results[clean_id] = title_a * score
            else:
                if zone == "c": # Content
                    new_results[clean_id] += content_a * score
                else: # Title
                    new_results[clean_id] += title_a * score

        results = list(new_results.items())
        results.sort(key=lambda x: x[1], reverse=True)
        
        write_result(r_file, results)

def write_result(r_file, documentId_score_pairs):
    """
    Writes results of documentId_score pairs into results file
    Args:
        r_file (str): File path of output result file
        documentId_score_pairs: List of documentId_score pairs
    """
    for id, _ in documentId_score_pairs:
        r_file.write(str(id) + " ")


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
