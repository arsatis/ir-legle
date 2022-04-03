This is the README file for A0188493L-A0218271J's submission
Email(s): e0324077@u.nus.edu
          e0544307@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

The high level idea of the indexing program is to:
1. Create dictionary with terms as key and the list of document IDs (postings) as values.
2. Store the dictionary's terms, frequency, and postings metadata in dictionary-file, and the list
   of document IDs in posting-file.

We make the following assumptions for indexing:
- The universe of document IDs can fit in memory. This is because we will use this information for
  operations such as NOT. If this was not allowed, we could have also stored a "partial" universe
  blocks in another file on disk. We then also similarly combine these universe blocks into a single
  sorted list. However during searching we will have to use the full universe list again for NOT
  operations

The first step would be to build a dictionary for the reuter dataset, by iterating through each
term in each sentence in each document in a target dataset.

In this program, it preprocesses each of theses term using case-folding and Porter-Stemming before
inserting them into the dictionary and appending the current document's ID into the posting list.

If the number of insertions hits the "memory limit", dictionary and posting list are dumped
into blocks into a block-temporary-file and resume adding the terms will end of all documents.

The next step would be to retrieve every pair of blocks from the block-temporary-file and merge the
posting lists into one using SPIMI. Each newly merged blocks are then appended to the end of the
block-temporary-file.

Lastly, every posting list are extracted from the final block from block-temporary-file. The posting
list are then converted to skip lists of document ID nodes that contains skips every math.sqrt(n).
These skip list are then written into the posting-file and the offset and size (metadata) of where
the skip list is dumpped to is stored in a dictonary of the current posting term as key and metadata
as value. This dictionary of all the posting terms and their metadata are then stored into the
dictionary-file.

Additional information of how we determine our "memory limit":
Let our memory limit be N. 
Calculations are made with calls to `sys.getsizeof()`
A Python int occupies 28 bytes. Assume a 64-bit machine, so we need 8 bytes for every pointer
to the list of arrays.
An average word length in English is 5 characters long --> 54 Bytes.
Thus key + value = 54 + 8 = 62 bytes
Assume a very pessimistic view that out of the N entries we will write, only N/2 are distinct.
Total memory usage:
N/2*62 + N*28 = 59N Bytes
In our program, we set a memory limit of ~7/8MB --> 
2^3 N = 2^20 bytes
    N = 2^17
      = 131072

While we understand that ~7/8 MB limit is unrealistically small compared to modern machines,
since the reuters data set is relatively small, setting a larger memory limit will not demonstrate
the merging behaviour. Thus we keep it this size so that we have a reasonable number of blocks.

We also wish to make a remark that the logic of merging blocks and merging posting lists is very
similar to the Merge algorithm. While it could have been abstracted to a function with another param,
we deliberately chose not to for several reasons:
1. The Merge Blocks algorithm involve opening file pointers. To which we have to seek, write, and calls
   pickles accordingly. This might not be easy to encapsulate as a higher-order function and it might even
   be inefficient because we open and potentially close files. (And if we don't close the files, we leak
   resources)
2. To communicate the intent of the function through its name. If we abstracted a higher-order function of
   Merge, it might not be immediately clear what the different calls to Merge was intended for.
3. It was a deliberate choice to perform the Merge algorithm for the merging of posting lists to be more efficient.
   A naive one-liner solution could have been to just add both lists to a set (eliminate duplicate) 
   and output the sorted list as the postings list. Although efficiency in indexing is not a concern,
   we performed the merge step in order to hopefully reflect better the implementation of SPIMI

We will now discuss the program for search.
The high level idea of the searching program is to:
1. Load data from the dictionary-file.
2. Process each query from query-file against the dictionary and postings. For each term, retrieve
   the corresponding metadata for that term from the postings-file.
3. Write the results of the queries to output-file

We make the following assumptions for searching:
- The full postings-file cannot be loaded into memory (homework requirement)
- The dictionary-file can be loaded into memory (homework requirement)
- The intermediate postings can all be loaded into memory (if this was not allowed, we could
have written the intermediate postings to disk, but since speed is a concern we make this assumption
so as not to degrade performance)

The first step of searching is to load the dictonary from dictionary-file into memory and only
opens postings-file file pointer. Note, full postings are not loaded like dictonary.

Next step, we iterate through all queries (lines in query-file) and preprocess and tokenize its
terms using case-folding and Porter-Stemming parsing the list of terms and query operators from
infix order to postfix order using Shunting-Yard. 

Following the postfix order, the postfix list are read from left-to-right where each element is
checked if its an operator or term. If it is a term, the skip list is retrieved from the
posting-file using the metadata retrieved from the dictonary. The retrieved skip list is then
inserted in a stack of postings. Else if it is a binary operator like AND and OR, the stack of
postings is popped twice to operate the AND or OR. Otherwise, it is a unary operator for NOT where
only the stack is popped once and is operated together with all document IDs (universe). 

The final posting list is then returned and is written to the output-file.

== Files included with this submission ==

- index.py       : Code implementation for indexing a directory to dictionary and posting files
- parser.py      : Code implementation for parsing infix queries to postfix format
- dictionary.txt : Encoded data file containing the dictionary that maps to the metadata of the postings
- postings.txt   : Encoded data file containing all posting lists of reuters dataset
- query.py       : Code implementation for QueryProcessor class
- README.txt     : This file
- search.py      : Code implementation for executing search
- skip_list.py   : Code implementation for skip_list class 
- tokeniser.py   : Code implementation for Tokeniser class for queries

Note: We have NaiveQueryProcessor and OptimisedQueryProcessor in query.py. The Optimised implementation
is the one that is being used, and NaiveQueryProcessor is only used for correctness benchmarks.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0188493L-A0218271J, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0188493L-A0218271J, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

- http://en.wikipedia.org/wiki/Shunting-yard_algorithm  : Shunting Yard pseudocode
- https://docs.python.org/3.7/library/pickle.html       : Pickle file usage
- https://docs.python.org/3/tutorial/inputoutput.html   : File handler usage (seek, read, tell)
