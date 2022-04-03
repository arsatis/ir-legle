#!/usr/bin/python3
import sys
import getopt
import pickle

from tokeniser import Tokeniser
from parser import Parser
from query import OptimisedQueryProcessor


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
    with open(dict_file, 'rb') as f:
        dictionary, universe_data = pickle.load(f)

    posting = open(postings_file, 'rb')

    print('running search on the queries...')

    with open(queries_file, 'r') as q_file, open(results_file, 'w') as r_file:
        tokeniser = Tokeniser()
        parser = Parser()
        processer = OptimisedQueryProcessor()

        for query in q_file:
            if query.strip() == "":
                continue
            # Process each query line
            tokens = tokeniser.tokenise(query)
            try:
                postfix_query = parser.to_postfix(tokens)
                result_query = processer.process(postfix_query, dictionary, posting, universe_data)
            except AssertionError:
                # failed some assertion errors. Either in Shunting-Yard
                # or while processing
                result_query = []
            except Exception:
                result_query = []
            finally:
                # Write to result file
                for i in result_query:
                    r_file.write(str(i) + " ")
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
