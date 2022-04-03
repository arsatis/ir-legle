#!/usr/bin/python3
import re
import sys
import os
import getopt
import pickle
import skip_list
import itertools

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import deque


# Counts the total number of entries read
MEMORY_BLOCK_LIMIT = 131072 
BLOCK_FILENAME = "blockstemp"


def create_blocks(in_dir):
    """
    Reads all files in directory and creates dictionary of terms in each text and posting list of
    documentIds where term is located. Writes dictionary and posting data into temporary file.
    Creates queue of list of blocks (position of data in temporary file and size of data) 
    and list of all documentIds in the directory (postings).
    Args:
        in_dir (str): File path of input directory
    Returns:
        block_queue (deque): Queue of list of blocks
        universe (list): List of all documentIds
    """

    universe = []
    term_dict = {}
    stemmer = PorterStemmer()
    write_to_disk_count = itertools.count() # for printing information

    # Queue of lists, where each list has (pos, len) information of a tuple in a specific block
    # First list in queue represents the first block. And the n elements in the list, represents
    # the n elements (in order) in that block.
    # (pos, len) will be used to seek and read from the disk
    block_queue = deque()

    def write_to_disk(term_dict):
        """
        Writes dictionary and posting data into temporary file 
        Args:
            term_dict (dict): Dictionary of terms containing postings
        Returns:
            block_order (list): List of blocks 
        """ 
        next(write_to_disk_count)
        sorted_term_posting_pairs = sorted(term_dict.items())
        block_order = []
        with open(BLOCK_FILENAME, 'ab') as block_f:
            for entry in sorted_term_posting_pairs:
                pos = block_f.tell()
                size = block_f.write(pickle.dumps(entry))
                block_order.append((pos, size))
        
        return block_order

    # Iterate directory in numerical order
    num_entries_read = 0
    file_number = itertools.count(1)
    for filename in sorted(os.listdir(in_dir), key=int):
        universe.append(int(filename))
        c = next(file_number)
        if c % 500 == 0:
            print(f"files read: {c}")

        with open(os.path.join(in_dir, filename), 'r') as f:
            for uncleaned_sentence in sent_tokenize(f.read()):
                # Remove special characters
                sentence = re.sub('[^ \w+]','', uncleaned_sentence)
                for unstemmed_word in word_tokenize(sentence):
                    # Porter Stemmer + Case-fold
                    word = stemmer.stem(unstemmed_word.lower())
                    if word in term_dict:
                        if int(filename) not in term_dict[word]:
                            term_dict[word].append(int(filename))
                        else:
                            continue
                    else:
                        term_dict[word] = [int(filename)]

                    # counter up.
                    num_entries_read += 1
                    # once we hit the limit. Write to block
                    # then reset the memory block counter. Add a new entry to the queue
                    if num_entries_read >= MEMORY_BLOCK_LIMIT:
                        block_order = write_to_disk(term_dict)
                        block_queue.append(block_order)
                        # resetting values to read the next block
                        term_dict = {} 
                        num_entries_read = 0

    if num_entries_read > 0: # have things to write
        block_order = write_to_disk(term_dict)
        block_queue.append(block_order)
    
    print(f"Blocks written to disk: {next(write_to_disk_count)}")
        
    return (block_queue, universe)


def merge_blocks(block_queue):
    """
    Merges blocks of position of data in temporary file and write size of data with each other into
    a single block
    Args:
        block_queue (deque): Queue of list of blocks
    """ 
    def merge_posting_list(posting_A, posting_B):
        """
        Merges 2 posting lists into 1. Combines every posting between both list.
        Args:
            posting_A (list): List of postings of term
            posting_B (list): List of postings of term
        Returns:
            answer (list): Merged list of postings
        """ 
        answer = []
        index_A, index_B = 0, 0
        while index_A < len(posting_A) and index_B < len(posting_B):
            if posting_A[index_A] == posting_B[index_B]:
                answer.append(posting_A[index_A])
                index_A += 1
                index_B += 1
            elif posting_A[index_A] < posting_B[index_B]:
                answer.append(posting_A[index_A])
                index_A += 1
            else:
                answer.append(posting_B[index_B])
                index_B += 1

        # Flush remaining postings
        while index_A < len(posting_A):
            answer.append(posting_A[index_A])
            index_A += 1

        while index_B < len(posting_B):
            answer.append(posting_B[index_B])
            index_B += 1

        return answer

    def pairwise_block_merge(block_A, block_B):
        """
        Merges 2 blocks into 1. Combines every posting of each term between both list.
        Args:
            block_A (list): List of blocks from temporary file
            block_A (list): List of blocks from temporary file
        Returns:
            block_order (list): Merged list of blocks
        """ 
        index_A = 0
        index_B = 0
        block_order = []
        with open(BLOCK_FILENAME, 'ab+') as f:
            while index_A < len(block_A) and index_B < len(block_B):
                pos_A, size_A = block_A[index_A]
                pos_B, size_B = block_B[index_B]

                # need to append the results
                append_end_pos = f.tell()

                # read from Block A
                f.seek(pos_A)
                term_A, posting_A = pickle.loads(f.read(size_A))

                f.seek(pos_B)
                term_B, posting_B = pickle.loads(f.read(size_B))
                if term_A == term_B:
                    to_write = (term_A, merge_posting_list(posting_A, posting_B))
                    index_A += 1
                    index_B += 1
                elif term_A < term_B:
                    to_write = (term_A, posting_A)
                    index_A += 1
                else:
                    to_write = (term_B, posting_B)
                    index_B += 1
                
                f.seek(append_end_pos)
                size_written = f.write(pickle.dumps(to_write))
                block_order.append((append_end_pos, size_written))
            
            # Flush remaining blocks
            while index_A < len(block_A):
                append_end_pos = f.tell()
                pos_A, size_A = block_A[index_A]
                f.seek(pos_A)
                to_write = pickle.loads(f.read(size_A))

                f.seek(append_end_pos)
                size_written = f.write(pickle.dumps(to_write))
                block_order.append((append_end_pos, size_written))
                index_A += 1

            while index_B < len(block_B):
                append_end_pos = f.tell()
                pos_B, size_B = block_B[index_B]
                f.seek(pos_B)
                to_write = pickle.loads(f.read(size_B))

                f.seek(append_end_pos)
                size_written = f.write(pickle.dumps(to_write))
                block_order.append((append_end_pos, size_written))
                index_B += 1

            return block_order

    num_blocks_merged = itertools.count(1)
    while len(block_queue) > 1:
        block_A = block_queue.popleft()
        block_B = block_queue.popleft()

        c = next(num_blocks_merged)
        if c % 50 == 0:
            print(f"pairs of block merged: {c}. remaining: {len(block_queue)}")

        resulting_block_order = pairwise_block_merge(block_A, block_B)
        block_queue.append(resulting_block_order)


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    Builds index from documents stored in the input directory, then output the dictionary file and postings file
    Args:
        in_dir (str): File path of input directory
        out_dict (str): File path of output dictionary
        out_postings (str): File path of output posting
    """

    print('indexing...')
    dictionary_file = {}

    block_queue, universe = create_blocks(in_dir)
    assert len(block_queue) >= 1
    print("finished creating blocks")
    merge_blocks(block_queue) # mutates block_queue
    print("finished merging blocks")
    assert len(block_queue) == 1
    final_block_order = block_queue.popleft()

    with open(out_postings, 'wb') as posting_f:
        print("writing block orders")
        # Write each term's posting list
        with open(BLOCK_FILENAME, 'rb') as block_f:
            for entry_pos, entry_size in final_block_order:
                block_f.seek(entry_pos)
                term, posting = pickle.loads(block_f.read(entry_size))

                skip_posting = skip_list.create_skip_list_from_docid_list(posting)
                assert len(skip_posting) == len(posting)

                written_pos = posting_f.tell()
                written_size = posting_f.write(pickle.dumps(skip_posting))
                dictionary_file[term] = (len(skip_posting), written_pos, written_size)

        # Write universe
        pos = posting_f.tell()
        size = posting_f.write(pickle.dumps(skip_list.create_skip_list_from_docid_list(universe)))
        universe_data = (len(universe), pos, size)

    with open(out_dict, 'wb') as f:
        # Write term dictonary 
        pickle.dump((dictionary_file, universe_data), f, pickle.HIGHEST_PROTOCOL)
    
    os.remove(BLOCK_FILENAME) # cleanup

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

# Ensures that input names do no overwrite temporary file
if BLOCK_FILENAME == output_file_postings or BLOCK_FILENAME == output_file_dictionary:
    print(f"Please do not use {BLOCK_FILENAME}")
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)