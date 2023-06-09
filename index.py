#!/usr/bin/python3
import csv
import sys
import getopt
import pickle
import collections
import math
import time
import re

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from datetime import timedelta

# CSV Column Index
ID = 0
TITLE = 1
CONTENT = 2
COURT = 4

# Court names with high importance
H_courts = set(["SG Court of Appeal", "SG Privy Council", "UK House of Lords", "UK Supreme Court",
                "High Court of Australia", "CA Supreme Court"])

# Court names with medium importance
M_courts = set(["SG High Court", "Singapore International Commercial Court", "HK High Court", 
                "HK Court of First Instance", "UK Crown Court", "UK Court of Appeal", "UK High Court",
                "Federal Court of Australia", "NSW Court of Appeal", "NSW Court of Criminal Appeal", "NSW Supreme Court"])

def init_csvreader():
    """
    Initializes CSV Reader size. Allows for more rows to be read.
    Retrieved from: https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072.
    """
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)

def tabulate_dictionary(term_dict, doc_weight, entry, zone):
    """
    Tabulates the term frequency and term position of an entry's column.
    Args:
        term_dict  (dict): Dictionary of terms to postings
        doc_weight (dict): Dictionary of documents to weights
        entry      (list): Entry data of current CSV row
        zone       (int) : Entry column index to be tabulated
    """
    data = entry[zone]

    # Changes doc_id based on zone chosen
    # .t == title zone
    # .c == content zone
    if zone == TITLE:
        doc_id = entry[ID] + '.t'
    elif zone == CONTENT:
        doc_id = entry[ID] + '.c'
    else:
        raise Exception('No such zone')

    # Zero-index positions of terms
    word_pos = 0
    lemmatizer = WordNetLemmatizer()
    doc_dic = collections.defaultdict(int)
    for uncleaned_sentence in sent_tokenize(data):
        # Remove trailing special characters + Case-fold
        sentence = uncleaned_sentence.strip().lower()

        for unlemmatized_word in word_tokenize(sentence):
            # Verb lemmatization
            term = lemmatizer.lemmatize(unlemmatized_word, pos = "v")

            doc_dic[term] += 1
            if term in term_dict.keys():
                # Increment term
                freq, posting = term_dict[term]
                last_id, last_freq = posting[-1]

                if last_id == doc_id:
                    last_freq.append(word_pos)
                    posting[-1] = (last_id, last_freq)
                else:
                    posting.append((doc_id, [word_pos]))
                    freq += 1

                term_dict[term] = (freq, posting)
            else:
                # Create tuple of freq and posting of term
                term_dict[term] = (1, [(doc_id, [word_pos])])
                
            word_pos += 1

    court = entry[COURT]
    if court in H_courts:
        importance = "H"
    elif court in M_courts:
        importance = "M"
    else:
        importance = "L"

    # Compute document length
    weighted_tfs = []
    for term in doc_dic:
        weighted_tfs.append(1 + math.log10(doc_dic[term]) if doc_dic[term] >= 1 else 0)
    doc_length = math.sqrt(sum([x * x for x in weighted_tfs]))

    doc_weight[doc_id] = (doc_length, importance)

def create_dictionary(in_dir):
    """
    Reads all entries in CSV and creates dictionary of terms in each document/zone, posting list of
    documentId zones and positioning where term is located, and dictionary of term-length in each
    document/zone.
    Args:
        in_dir      (str): File path of input CSV
    Returns:
        term_dict  (dict): Dictionary of terms to postings
        doc_weight (dict): Dictionary of documents to weights
    """
    def isChinese(entry):
        """
        Checks if the entry contains Chinese characters.
        Refer to https://unicode-table.com/en/blocks/ for unicode ranges.
        Args:
            entry (list): Row/entry data of dataset
        Returns:
               (boolean): True if contains Chinese, else False
        """
        # CJK Unified Ideographs
        checker = re.compile(r'[\u4e00-\u9fff]+')
        return checker.match(entry[TITLE]) != None
    
    term_dict = {}
    doc_weight = {}

    with open(in_dir, 'r', encoding="utf8") as f:
        # Read rows into a dictionary format
        # Format: document_id, title, content, date_posted, court
        reader = csv.reader(f) 
        
        # Skip header
        next(reader) 
        
        for entry in reader:
            if isChinese(entry):
               continue
            tabulate_dictionary(term_dict, doc_weight, entry, TITLE)
            tabulate_dictionary(term_dict, doc_weight, entry, CONTENT)

    return (term_dict, doc_weight)

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    Builds index from documents stored in the input directory, then output the dictionary file and postings file
    Args:
        in_dir       (str): File path of input directory
        out_dict     (str): File path of output dictionary
        out_postings (str): File path of output posting
    """
    print('indexing...')

    init_csvreader()
    
    dictionary_file = {}
    term_dict, doc_weight = create_dictionary(in_dir)

    with open(out_postings, 'wb') as posting_f:
        # Write each term's posting list
        for term, posting in term_dict.items():
            written_pos = posting_f.tell()
            written_size = posting_f.write(pickle.dumps(posting))
            dictionary_file[term] = (posting[0], written_pos, written_size)

    with open(out_dict, 'wb') as f:
        # Write term dictonary and document weights
        pickle.dump((dictionary_file, doc_weight), f, pickle.HIGHEST_PROTOCOL)

input_dataset = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input dataset
        input_dataset = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_dataset == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

# Track time taken for indexing
start = time.time()
build_index(input_dataset, output_file_dictionary, output_file_postings)
end = time.time()
print('Time Taken:', str(timedelta(seconds=math.ceil(end - start))))
