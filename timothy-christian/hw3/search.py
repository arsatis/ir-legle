#!/usr/bin/python3
import sys
import getopt
from model import VectorSpaceModel
from parser import FreeTextParser

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
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

    model = VectorSpaceModel(dict_file, postings_file)
    parser = FreeTextParser()
    with open(queries_file, 'r') as q_file, open(results_file, 'w') as r_file:
        for query in q_file:
            if query == "":
                continue
            query_detail = parser.to_query_detail(query)
            score_id_pairs = model.cosine_score(query_detail, 10)
            write_result(r_file, score_id_pairs)

def write_result(r_file, score_id_pairs):
    """
    Writes results of score-documentId pairs into results file
    Args:
        r_file (str): File path of output result file
        score_id_pairs: List of score-documentId pairs
    """
    for _, doc_id in score_id_pairs:
        r_file.write(str(doc_id) + " ")
    r_file.write("\n")

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
