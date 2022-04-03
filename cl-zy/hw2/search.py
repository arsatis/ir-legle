#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
import ast
import os

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # for debugging purposes, remove results_file everytime search is executed
    if os.path.isfile(results_file):
        os.remove(results_file)

    dic = {}
    with open(dict_file, 'rb') as file:
        dic = pickle.load(file)

    with open(queries_file) as file:
        for query in file:
            operationStack = []
            outputQueue = []

            query = nltk.word_tokenize(query)
            query = order_NOT_queries(query) # if query is : NOT NOT a...
            query = order_AND_queries(query, dic) # if query has consecutive ANDs: a AND b AND c...

            prevType = None

            # Shunting-yard algo
            for term in query:
                if term == "(":
                    prevType = "opr"
                    operationStack.append(term)
                elif term == "NOT":
                    prevType = "opr"
                    outputQueue.append("*")
                    operationStack.append(term)
                elif term == "AND":
                    prevType = "opr"
                    while (len(operationStack) != 0 and operationStack[-1] == "NOT"):
                        outputQueue.append(operationStack.pop())
                    operationStack.append(term)
                elif term == "OR":
                    prevType = "opr"
                    while (len(operationStack) != 0 and (operationStack[-1] == "AND" or operationStack[-1] == "NOT")):
                        outputQueue.append(operationStack.pop())
                    operationStack.append(term)
                elif term == ")":
                    prevType = "opr"
                    while (operationStack[-1] != "("):
                        outputQueue.append(operationStack.pop())
                    operationStack.pop()
                else: # word term, same preprocessing as index
                    # stemming + case-folding
                    if (prevType == "word"):
                        prevType = "invalid"
                        break
                    else:
                        prevType = "word"
                        ps = nltk.stem.PorterStemmer()
                        term = ps.stem(term.lower())
                        outputQueue.append(term)

            if prevType == "invalid":
                with open(results_file, 'a') as write_results_file: 
                    write_results_file.write("\n")
            else:
                while (len(operationStack) != 0):
                    outputQueue.append(operationStack.pop())

                reversePolishStack = []
                while (len(outputQueue) > 0 and outputQueue[0] != "NOT" and outputQueue[0] != "AND" and outputQueue[0] != "OR"):
                    reversePolishStack.append(outputQueue.pop(0))

                result = []
                isSingleTerm = False
                while not (len(reversePolishStack) == 1 and reversePolishStack[0] == "$" and len(outputQueue) == 0):
                    # single term query, no operators
                    if (len(outputQueue) == 0 and len(reversePolishStack) == 1):
                        subquery = reversePolishStack[0]
                        isSingleTerm = True
                    else:
                        # [operator, wordTermA, wordTermB]
                        subquery = [outputQueue.pop(0), reversePolishStack.pop(), reversePolishStack.pop()]
                    result = processSubquery(subquery, dic, postings_file, result)

                    if (isSingleTerm):
                        break
                    else:
                        reversePolishStack.append("$")
                        while (len(outputQueue) > 0 and outputQueue[0] != "NOT" and outputQueue[0] != "AND" and outputQueue[0] != "OR"):
                            reversePolishStack.append(outputQueue.pop(0))

                with open(results_file, 'a') as write_results_file:
                    result = " ".join(map(str, result[0])) 
                    write_results_file.write(result + "\n")

def order_NOT_queries(query):
    # find position of NOTs
    pos_list = [i for i in range(len(query)) if query[i] == "NOT" and (i - 1 >= 0 and query[i - 1] != "(")]

    # check for locations with two consecutive NOTs in a row
    if pos_list:
        idx = len(pos_list) - 1
        while idx > 0:
            if pos_list[idx] - pos_list[idx - 1] > 2: # not consecutive
                idx -= 1
            else:
                # remove them from query
                query.pop(pos_list[idx])
                query.pop(pos_list[idx - 1])
                idx -= 2
                
    return query

def order_AND_queries(query, dic):
    # find position of ANDs
    pos_list = [i for i in range(len(query)) if query[i] == "AND" and (i - 2 >= 0 and query[i - 2] != "NOT")]

    # check for locations with two or more consecutive ANDs in a row
    if pos_list:
        idx = 1
        while idx < len(pos_list):
            if pos_list[idx] - pos_list[idx - 1] > 2 \
                or re.match(r'\W+', query[pos_list[idx - 1] - 1]) \
                or re.match(r'(\W+)|(NOT)', query[pos_list[idx - 1] + 1]):
                # not consecutive
                idx += 1
            else:
                # find how many are there in a row
                k = 0
                while idx + k + 1 < len(pos_list) and pos_list[idx + k + 1] - pos_list[idx + k] == 2:
                    k += 1
                
                # order terms in ascending order based on size of posting list
                terms = [query[pos_list[i] - 1] for i in range(idx - 1, idx + k + 1)] + [query[pos_list[idx + k] + 1]]
                terms.sort(key=lambda x: dic[x][2] if x in dic.keys() else 0, reverse=True)
                for i in range(len(terms) - 1):
                    query[pos_list[idx + i - 1] - 1] = terms[i]
                query[pos_list[idx + k] + 1] = terms[-1]

                # increment idx
                idx += (k + 2)
                
    return query

def retrieveSkipPtrsAndLst(postingPtr, sizeOfPosting, postings_file):
   with open(postings_file) as file:
        file.seek(postingPtr)
        skipPtrsAndLst = file.read(sizeOfPosting)
        return ast.literal_eval(skipPtrsAndLst)

def processSubquery(subquery, dic, postings_file, result):
    subqueryResult = []
    operator = subquery[0]

    # single word term, no operators
    if operator != "NOT" and operator != "AND" and operator != "OR":
        term = subquery
        if term in dic:
            termPostingSkipPtrsAndLst = retrieveSkipPtrsAndLst(dic[term][1], dic[term][2], postings_file)
            result.append(termPostingSkipPtrsAndLst[1])
            return result
        else:
            result.append(subqueryResult)
            return result
    
    if operator == "NOT":
        term = subquery[1]
        termSkipPtrs = {}
        termPostingLst = []
        
        reuterFileIds = list(filter(lambda doc: doc.startswith("training/"), nltk.corpus.reuters.fileids()))
        for i in range(0, len(reuterFileIds)):
            reuterFileIds[i] = int(reuterFileIds[i].split('/')[-1])
        reuterFileIds.sort()

        if term == "$": # use previously calculated result
            termPostingLst = result.pop()
        elif term in dic:
            termPostingSkipPtrsAndLst = retrieveSkipPtrsAndLst(dic[term][1], dic[term][2], postings_file)
            termSkipPtrs = termPostingSkipPtrsAndLst[0]
            termPostingLst = termPostingSkipPtrsAndLst[1]
        else:
            result.append(reuterFileIds)
            return result

        ptrTerm = 0
        ptrAll = 0
        
        while ptrAll < len(reuterFileIds) and ptrTerm < len(termPostingLst):
            if termPostingLst[ptrTerm] == reuterFileIds[ptrAll]:
                reuterFileIds.pop(ptrAll)
                ptrTerm += 1
            elif termPostingLst[ptrTerm] < reuterFileIds[ptrAll]:
                if ptrTerm in termSkipPtrs and termPostingLst[termSkipPtrs[ptrTerm]] <= reuterFileIds[ptrAll]:
                    while ptrTerm in termSkipPtrs and termPostingLst[termSkipPtrs[ptrTerm]] <= reuterFileIds[ptrAll]:
                        ptrTerm = termSkipPtrs[ptrTerm]
                else:
                    ptrTerm += 1
            else:
                ptrAll += 1

        subqueryResult = reuterFileIds        

    else:
        termA = subquery[1]
        termB = subquery[2]
        termAPostingLst = []
        termBPostingLst = []
        termASkipPtrs = {}
        termBSkipPtrs = {}

        if termB == "$":
            termBPostingLst = result.pop()
        elif termB in dic:
            termBPostingSkipPtrsAndLst = retrieveSkipPtrsAndLst(dic[termB][1], dic[termB][2], postings_file)
            termBSkipPtrs = termBPostingSkipPtrsAndLst[0]
            termBPostingLst = termBPostingSkipPtrsAndLst[1]

        if termA == "$":
            termAPostingLst = result.pop()
        elif termA in dic:
            termAPostingSkipPtrsAndLst = retrieveSkipPtrsAndLst(dic[termA][1], dic[termA][2], postings_file)
            termASkipPtrs = termAPostingSkipPtrsAndLst[0]
            termAPostingLst = termAPostingSkipPtrsAndLst[1]
            
        if operator == "AND":
            if (termA != "$" and termA not in dic) or (termB != "$" and termB not in dic):
                result.append(subqueryResult)
                return result

            ptrA = 0
            ptrB = 0
            while ptrA < len(termAPostingLst) and ptrB < len(termBPostingLst):
                if termAPostingLst[ptrA] == termBPostingLst[ptrB]:
                    subqueryResult.append(termAPostingLst[ptrA])
                    ptrA += 1
                    ptrB += 1
                elif termAPostingLst[ptrA] < termBPostingLst[ptrB]:
                    if ptrA in termASkipPtrs and termAPostingLst[termASkipPtrs[ptrA]] <= termBPostingLst[ptrB]:
                        while ptrA in termASkipPtrs and termAPostingLst[termASkipPtrs[ptrA]] <= termBPostingLst[ptrB]:
                            ptrA = termASkipPtrs[ptrA]
                    else:
                        ptrA += 1
                else:
                    if ptrB in termBSkipPtrs and termBPostingLst[termBSkipPtrs[ptrB]] <= termAPostingLst[ptrA]:
                        while ptrB in termBSkipPtrs and termBPostingLst[termBSkipPtrs[ptrB]] <= termAPostingLst[ptrA]:
                            ptrB = termBSkipPtrs[ptrB]
                    else:
                        ptrB += 1

        elif operator == "OR": # skip ptrs not used
            if (termA != "$" and termA not in dic) and (termB != "$" and termB not in dic):
                result.append(subqueryResult)
                return result 

            ptrA = 0
            ptrB = 0
            while ptrA < len(termAPostingLst) and ptrB < len(termBPostingLst):
                if termAPostingLst[ptrA] == termBPostingLst[ptrB]:
                    subqueryResult.append(termAPostingLst[ptrA])
                    ptrA += 1
                    ptrB += 1
                elif termAPostingLst[ptrA] < termBPostingLst[ptrB]:
                    subqueryResult.append(termAPostingLst[ptrA])
                    ptrA += 1
                else:
                    subqueryResult.append(termBPostingLst[ptrB])
                    ptrB += 1
            
            # add remaining list
            if ptrA < len(termAPostingLst):
                subqueryResult += termAPostingLst[ptrA:]
            elif ptrB < len(termBPostingLst):
                subqueryResult += termBPostingLst[ptrB:]

    result.append(subqueryResult)
    return result

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
