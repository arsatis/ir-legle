This is the README file for A0188493L-A0218271J's submission
Email(s): e0324077@u.nus.edu
          e0544307@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

The high level idea of the indexing program is to:
1. Create 2 dictionaries. First, with terms as key and the dictionary of documentId with frequency
   of that term in occurrence as values ('posting'). Second, the other with documentId as key and
   dictionary of term with weight of that term as values ('weightage').
2. Store these dictionaries in dictionary-file, and the list of postings in posting-file.

We make the following assumptions for indexing:
- The dictionary of weightage can fit in memory. This is because we will be using this information
  for wtd (weight-term-document) during the search phase. If disallowed, we could have also stored
  this data structure the same way as dictionary is linked to posting via file size and offset.

The first step would be to build a dictionary for the reuter dataset, by iterating through each
term in each sentence in each document in a target dataset.

In this program, it preprocesses each of these terms using case-folding and Porter-Stemming before
inserting them into the term dictionary and incrementing the current document's term frequency
counter. Additionally, each document ID is also inserted into the weightage dictionary and
increments the term-frequency counter. 

After which the program converts the term-frequency of weightage dictionary into weights of the
terms in each document. This is done by iterating through each documentId and its terms, finding
their weights (which does tf logarithm) and then normalizing the resulant weights with the sqrt
sum of weights^2.

Note: In this program, we have pre-calculated the weights of each terms and normalized them in
indexing phase. This is because if we were to obtain the sqrt sum of weights^2 during search phase,
we may be recomputing the same normalization length to be divided repeatedly. Thus, this program
avoids such cases by computing the normalization once per document and applies it to all terms 
belonging to the document. Hence, doing this computation here reduces the processing time of search
and is not heavy impact since indexing step is not as time-sensitive as search.

Lastly, the posting dictionary is then iterated to extract each final posting and written to 
postings-file, having its written size and position stored as a 'pointer' in a dictionary. This new
dictionary and weightage dictionary is then written to the dictionary-file.

We will now discuss the program for search.
The high level idea of the searching program is to:
1. Load data from the dictionary-file while keeping a file pointer to postings-file.
2. Process each query from query-file into a set of K most relevant documents.
3. Write the results of the queries to output-file.

We make the following assumptions for searching:
- The full postings-file cannot be loaded into memory (homework requirement)
- The dictionary-file can be loaded into memory (if both dictionaries are was not allowed, we could
  have written the weighage dictionary to disk, but since speed is a concern we make this
  assumption so as not to degrade performance)

The first step of searching is to load the dictonary from dictionary-file into memory and only
opens postings-file file pointer. Note, full postings are not loaded like dictonary.

Next step, we iterate through all queries (lines in query-file) and preprocess and parse its terms
using case-folding and Porter-Stemming, resulting in a dictionary of query terms and its frequency
occurrences within the query line.

Following the parsing, the terms in each query dictionary are then used to compute their cosine
scores. Each term is processed to find its weights (which does tf logarithm calculation * inverse
document frequency -- idf) and then normalizing the resulant weights with the sqrt sum of
weights^2. Next, each query-term-weight then retrieves the document weights of all postings where
the term exist in the document, and sums the multiplication of query weight with document weight.
Thus, getting the final cosine score.

These cosine scores are then inserted in the a heap which only keeps the top 10 scores in its list.
After which, these 10 scores are returned back and is written to the output file.

== Files included with this submission ==

- algorithm.py   : Code implementation for TopK class
- index.py       : Code implementation for indexing a directory to dictionary and posting files
- model.py       : Code implementation for VectorSpaceModel class
- parser.py      : Code implementation for parsing free text queries to terms and frequnecy
- dictionary.txt : Encoded data file containing the dictionary that maps to the metadata of the postings
- postings.txt   : Encoded data file containing all posting lists of reuters dataset
- README.txt     : This file
- search.py      : Code implementation for executing search
- weighting.py   : Code implementation for TermFrequency, DocumentFrequency, TfIdfWeight class

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0188493L-A0218271J, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] We, A0188493L-A0218271J, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
