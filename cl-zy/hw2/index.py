#!/usr/bin/python3
import nltk
import sys
import getopt
import os
import pickle
import math

from nltk.tokenize import sent_tokenize, RegexpTokenizer

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def spimi(in_dir, temp_dir):
    dir_list = sorted([int(x) for x in os.listdir(in_dir)])
    dir_idx = 0
    file_idx = 0

    while dir_idx < len(dir_list):
        mem = 100
        dic = {}

        while mem > 0:
            doc_id = dir_list[dir_idx]
            with open(in_dir + str(doc_id)) as file:
                # case-folding
                doc = file.read().lower()

                # tokenization
                tokenizer = RegexpTokenizer(r'\w+')
                tokens = [tokenizer.tokenize(d) for d in sent_tokenize(doc)]

                # stemming + appending into dict
                ps = nltk.stem.PorterStemmer()
                for sentence in tokens:
                    for i in range(len(sentence)):
                        term = ps.stem(sentence[i])
                        if term not in dic.keys():
                            # for each term: [number of postings, list of postings (doc_id)]
                            dic[term] = [1, [doc_id]]
                        else:
                            if len(dic[term][1]) == 0 or dic[term][1][-1] != doc_id:
                                dic[term][0] += 1
                                dic[term][1] += [doc_id]
            dir_idx += 1
            mem -= 1
            if dir_idx >= len(dir_list):
                break

        # sort dictionary terms (key) and convert it to a list
        sorted_terms = sorted(dic.items())

        # write block to disk
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        with open(temp_dir + str(file_idx), 'wb') as write_block:
            for term in sorted_terms:
                pickle.dump(term, write_block)
        file_idx += 1

def spimi_merge(temp_dir):
    dir_list = sorted([int(x) for x in os.listdir(temp_dir)])
    dir_idx = 0
    file_idx = 0
    num_pairs_to_read = 100

    # binary merge
    while dir_idx < len(dir_list):
        doc_id = dir_list[dir_idx]
        eof_x = False
        eof_y = False

        # if adjacent block does not exist
        if (doc_id + 1 >= len(dir_list)):
            with open(temp_dir + str(doc_id), 'rb') as file:
                with open(temp_dir + str(file_idx), 'wb') as write_block:
                    while True:
                        try:
                            x = pickle.load(file)
                            pickle.dump(x, write_block)
                        except:
                            break
            os.remove(temp_dir + str(doc_id))
            break

        # else, merge the two blocks
        file_x = open(temp_dir + str(doc_id), 'rb')
        file_y = open(temp_dir + str(doc_id + 1), 'rb')
        file_write = open(temp_dir + '-1', 'wb') # write to a temp file called -1
        x = []
        y = []
        while True:
            for i in range(num_pairs_to_read):
                try:
                    x.append(pickle.load(file_x))
                except:
                    eof_x = True
                    break

            for i in range(num_pairs_to_read):
                try:
                    y.append(pickle.load(file_y))
                except:
                    eof_y = True
                    break
                    
            # merging
            merge_list, x, y = partial_merge(x, y)

            # write block to disk
            for term in merge_list:
                pickle.dump(term, file_write)

            if eof_x and eof_y:
                break

        # check if there are any remaining unmerged pairs
        rem = x if len(x) > 0 else y
        for term in rem:
            pickle.dump(term, file_write)

        file_x.close()
        file_y.close()
        file_write.close()
        os.remove(temp_dir + str(doc_id))
        os.remove(temp_dir + str(doc_id + 1))

        # rename temp file to target file
        os.rename(temp_dir + '-1', temp_dir + str(file_idx))
        dir_idx += 2
        file_idx += 1

def partial_merge(x, y):
    """
    Instead of merging everything,
    returns the remaining parts of the array that are unmerged in the while loop in a tuple.
    """
    z = []
    x_idx = y_idx = 0
    while x_idx < len(x) and y_idx < len(y):
        x_term, y_term = x[x_idx][0], y[y_idx][0]
        if x_term < y_term:
            z.append(x[x_idx])
            x_idx += 1
        elif x_term > y_term:
            z.append(y[y_idx])
            y_idx += 1
        else:
            new_posting_size = x[x_idx][1][0] + y[y_idx][1][0]
            new_posting_list = x[x_idx][1][1] + y[y_idx][1][1]
            z_val = tuple([x_term, [new_posting_size, new_posting_list]])
            z.append(z_val)
            x_idx += 1
            y_idx += 1
    return tuple([z, x[x_idx:], y[y_idx:]])

def build_skip_ptrs(posting):
    num_skip_ptrs = math.floor(math.sqrt(len(posting)))
    interval = math.floor(len(posting) / num_skip_ptrs)
    ptr_dict = {}
    new_list = []
    for i in range(0, len(posting), interval):
        # key: index, value: nextSkipIndex
        if (i + interval < len(posting)):
            ptr_dict[i] = i + interval
    new_list.append(ptr_dict)
    new_list.append(posting)
    return new_list

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    temp_dir = "temp_files/"

    spimi(in_dir, temp_dir)
    while len(os.listdir(temp_dir)) > 1:
        spimi_merge(temp_dir)

    # extract dict and postings
    merged_posting_list = []
    with open(temp_dir + "0", 'rb') as file:
        while True:
            try:
                merged_posting_list.append(pickle.load(file))
            except:
                break
    dic = {}

    # delete postings and dictionary file everytime code is executed FOR DEBUGGING EASE
    if os.path.isfile(out_postings):
        os.remove(out_postings)
    if os.path.isfile(out_dict):
        os.remove(out_dict)

    for i in range(len(merged_posting_list)):
        dic[merged_posting_list[i][0]] = [merged_posting_list[i][1][0]]
        posting = merged_posting_list[i][1][1]

        # [{dict of skip pts}, [docIds]]
        posting_w_skip = build_skip_ptrs(posting)
        with open(out_postings, 'a') as write_file_post:
            dic[merged_posting_list[i][0]].append(write_file_post.tell())
            bytesWritten = write_file_post.write(str(posting_w_skip))
            dic[merged_posting_list[i][0]].append(bytesWritten)

    # write dict
    with open(out_dict, 'wb') as write_file_dict:
        pickle.dump(dic, write_file_dict)


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

