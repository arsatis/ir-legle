This is the README file for A0200025H and A0206154N's submission
Email(s): e0407006@u.nus.edu and e0426077@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

### `index.py`
* Pre-processing done: tokenization, case-folding and stemming (i.e., PorterStemmer)

We used SPIMI for indexing. We created a `temp_files/` directory to store our blocks.
We implemented the standard SPIMI algorithm with binary merging (i.e., we read 2 blocks by chunks and merge them).

After merging is done, skip pointers are generated for each posting list, where the _square root heuristic_ is used
to determine the position and quantity of skip pointers (i.e., we use `sqrt(len(posting))` number of evenly spaced skip pointers).

For the dictionary, entries were stored in the format `{ word_term: [posting_list_size, posting_file_pointer, num_of_bytes_written_for_posting] }`,
where `num_of_bytes_written_for_posting` is used to assist in reading the entry from disk.
Pickle was used to write our dictionary onto disk as `dictionary.txt`.

### `search.py`
* Pre-processing done: case-folding and stemming (same as `index.py`).

To process our queries, we used the Shunting-yard algorithm, which makes use of stacks and queues to process the query in
the right order. We converted unary `NOT a` to binary `* NOT a`.   

We also attempted to optimize several special cases of boolean queries which were covered in class, including:
* consecutive `AND` queries (e.g., `a AND B AND c`): posting size information from the dictionary is used to ensure that
  queries are processed in an ascending order, to make it more optimized.
* consecutive `NOT` queries (e.g., `NOT (NOT a)`): such queries were simplified to just `a` (i.e., the double negation is removed),
  in order to avoid the performing of unnecessary complement operations.

After the original query has been transformed into a reverse polish stack via the shunting-yard algorithm, we proceeded to process the subqueries.

1. For each subquery, we check the operator and whether any of the terms is a result from previous subqueries (denoted in our code as `$`).
2. If a term is not a result of previous subqueries, the posting list would be retrieved from `postings.txt`,
   and `seek()` and `read()` operations are used to obtain the specific posting list we require.
3. Next, we retrieve the skip pointers from the posting list, and run the "merge" algorithm. 
   Within the "merge" algorithm, skip pointers are utilized (except for `OR` queries). 
4. Subsequently, the results of the subquery are appended to the reverse polish stack.
5. Once the length of reverse polish stack is equals 1, the final result for the query is written to `output-file-of-results`.

This sequence of steps is repeated until all queries in `file-of-queries` are addressed.

== Files included with this submission ==

* `index.py`       - code for indexing of documents.
* `search.py`      - code for searching queries.
* `README.txt`     - this file.
* `dictionary.txt` - output of the dictionary from `index.py`.
* `postings.txt`   - output of all posting lists from `index.py`.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0200025H and A0206154N, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

* Shunting-yard algorithm (https://brilliant.org/wiki/shunting-yard-algorithm/)
