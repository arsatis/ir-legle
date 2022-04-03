This is the README file for A0200025H and A0206154N's submission
Email(s): e0407006@u.nus.edu and e0426077@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

Preprocessing:
- Word tokenisation
- Sentence tokenisation (only during indexing)
- Stemming (using the Porter stemmer)
- Case folding

# index.py
For each document in the Reuter training corpus, we performed the preprocessing steps as mentioned above.
Subsequently, each token was appended to the dictionary in the format: { term : [docFreq(df), posting list] }.
On the other hand, each posting list was formatted based on the suggestions provided on the module website, i.e.,: [(doc_id, termFreq(tf)), ...]
where each element in the list is a tuple containing the doc_id and tf.

For each document, we also calculated the doc length by:
1. Calculating weighted tfs for all the terms in the doc using: 1 + log10(tf)
2. Taking the sum of the squares of the weighted tfs

The total number of documents (N) is stored under the 'totalLength' key in the dictionary.

Towards the end of the indexing step, we stored everything to disk.
Specifically, we used Pickle for the dictionary, reuterIDs, and doc_length, and normal write for our file postings.

The dictionary will now have such a format: { term : [df, [startingPtr, bytesWritten]] }.


# search.py
Under search, our first step was to retrieve the dictionary, doc_length, reuterIDs.
To simplify our functions and reduce inefficiency, we defined several global variables, including: dic, N, dic_doc_length, and reuters_ids.
Specifically, we stored the 'totalLength' of the vocabulary as N, whereas the contents of the other variables could be inferred from their respective names.

We applied the same preprocessing methods (without sentence tokenisation) for the query, and passed the
token to vector_space_ranking function.

Within the vector_space_ranking function, we calculated the weighted tf-idf ((1 + log10(tf)) * log10(N / df)) for the query terms.
We also computed the weighted tf of each document for each query, and normalized both the query and document tf(idf) vectors.
Subsequently, we calculated the cosine similarity, where the query tf-idf and document tf of each term are multiplied.
Finally, the results are sorted in descending ordering based on their scores, and the top 10 documents are returned as output.

== Files included with this submission ==

- index.py          : code for indexing reuter's training corpus
- search.py         : code for processing queries
- README.txt        : this file
- dictionary.txt    : dictionary of indexed terms
- postings.txt      : file containing all the posting lists
- reuterIDs.txt     : list of all file ids in Reuter's training corpus
- doc_length.txt    : dictionary of calculated doc length for each docID, before doing sqrt

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0200025H and A0206154N, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

-

We suggest that we should be graded as follows:

-

== References ==

-
