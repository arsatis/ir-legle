This is the README file for A0188493L-A0218271J-A0200025H-A0206154N's submission.
Email(s): e0324077@u.nus.edu
          e0544307@u.nus.edu
	        e0407006@u.nus.edu
          e0426077@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

# Index

The high level idea of the indexing program is to:
1. Create 2 dictionaries. First, with terms as key and the dictionary of documentId with frequency
   of that term in occurrence as values ('posting'). Second, the other with documentId as key and
   dictionary of term with a pair of
    a) weight of that term as values ('weightage'),
    b) the importance of the court for this documentId.
2. Store these dictionaries in a dictionary-file, and the list of postings in a posting-file.

We make the following assumptions for indexing:
- The dictionary of weightage can fit in memory. This is because we will be using this information
  for wtd (weight-term-document) during the search phase. If disallowed, we could have also stored
  this data structure the same way as the dictionary is linked to posting via file size and offset.
- Dataset only contains English and Chinese documents.
- The documents and queries to be indexed and searched are in English only; documents which are not
  in English are ignored in our indexing.

The first step would be to build a dictionary for dataset.csv, by iterating through each term in
each sentence in each entry (row) in the target dataset. We will be indexing the "TITLE" and
"CONTENT" zones of each document. For each zone, we label the current zone being processed using a
string ".t" and ".c" for TITLE and CONTENT respectively rather than the full zone name, allowing us
to reduce the amount of bytes being written.

Note also in this iterative step, we skip Chinese documents by detecting if the TITLE contains
Chinese unicode characters from the CJK Unified Ideographs range.

For indexing, these are the preprocessing techniques we have used: 
- NLTK's sentence tokenization
- NLTK's word tokenization
- Case-folding 
- WordNetLemmatizer's lemmatization 

During our preprocessing, we deviated away from PorterStemmer and towards WordNetLemmatizer because
the latter preserves the semantics of the original text. On the other hand, the former simply
performs a crude "chopping" of the suffixes of words, and may not preserve the original meaning of
the word. As a result, using lemmas allows us to perform more language specific and contextual data
such as speech. Since the dataset being processed is made up of court cases, they are primarily
made up of text converted from spoken English rather than generic passages. Therefore, we take
advantage of the format of the data by using lemmatization and reduce them into verbs as they
contain the most semantic features in English. 

Furthermore, it is argued that lemmatization takes up more time to process compared to stemming;
however, during our experimentation, the time it took to index and search was about the same. Thus,
it should not heavily impact the performance of our index and search.

After preprocessing, we insert them into the term dictionary and increment the current document's
term frequency counter. Additionally, each document ID is also inserted into the weightage
dictionary and increments the term-frequency counter. Also, note that a word position counter is
incremented every term found per document so that each occurrence of a term would be inserted into
a positional posting list (zero-indexed).

After which the program converts the term-frequency of the weightage dictionary into weights of the
terms in each document. This is done by iterating through each documentId and its terms, finding 
their weights (i.e., log term frequency) and then normalizing the resultant weights with the 
sqrt(sum of weights^2).

Additionally, when iterating through each document, we categorize them based on the "Notes about 
Court Hierarchy" where those documents from court Most Important are labeled as H, Important as M
and Rest as L, representing the importance / relevance of that document. Since both weightage and
importance are associated directly to a document, the pair is stored in the same dictionary object.

Lastly, the posting dictionary is then iterated to extract each final posting and written to 
postings-file, having its written size and position stored as a 'pointer' in a pointer dictionary.
This new pointer dictionary, weightage-importance dictionary is then written to the dictionary-file.

# Search

We will now discuss the program for search.
The high level idea of the searching program is to:
1. Load data from the dictionary-file while keeping a file pointer to postings-file.
2. Process query from query-file.
3. Write the results of the queries to the output-file.

We make the following assumptions for searching:
- The full postings-file cannot be loaded into memory.
- The dictionary-file can be loaded into memory (if both dictionaries were not allowed, we could
  have written the weightage dictionary to disk, but since speed is a concern we make this
  assumption so as not to degrade performance).
- The quotation marks used for phrasal queries is " ", not “ ”.
- "AND" is reserved strictly for boolean queries.

The first step of searching is to load the dictionary from the dictionary-file into memory, and
access the file pointer to the relevant posting within the postings-file. Note that the postings
are not loaded in the same manner as the dictionary, due to the assumptions stated in the
previous paragraph.

For our next step, we will load the query-file and parse it in QueryDetails. 
In QueryDetails, these are the preprocessing techniques we have used: 
- NLTK's word tokenization
- Case-folding 
WordNetLemmatizer's lemmatization 

Subsequently, it will check for the type of the query, which is either boolean, phrasal, or
free-text. It detects boolean queries via the "AND" keyword, and phrasal queries via its quotation
marks. We also perform some basic error checking, including invalid placement of "AND"s. If the
query is invalid, the program will immediately return an empty line in the output file.

If the query type is not "free-text", we will convert it to "free-text" as the rigid boolean query
algorithm does not return desirable results based on our experiments. Even though a positional index
was constructed in our indexing step, this was not utilized subsequently for phrasal queries, due to
our conversion of all query types to "free-text".

For query refinement, we implemented query expansion. Our implementation is a hybrid of NLTK
Wordnet's synsets and our manually curated synonym set. For every term in the query, we will first
check if we recognise the word (i.e., whether it is part of our custom synset). If we recognise it,
we will expand it using the associated custom set of words that we have. If not, we will rely on
NLTK Wordnet's synonym sets. We use a similarity score to rank the synonym sets, and then take the
first k synonyms (not synonym sets) to expand the terms, so that the query does not drift.

The custom set of words are curated from reading through the documents, and attempting to
understand the context and grouping together words that frequently come together in the same
context (cf. distributional hypothesis). We feel that this should be more informative in the
context of legal case retrieval than relying on a generic thesaurus, since our goal is to build a
system for the specific purpose of legal case retrieval, thus it should make sense to make an
attempt at optimisation by studying the nature of the documents.

We also explored pseudo-relevance feedback, but it is no longer part of submission due to its
lackluster performance. However, more details can be found in BONUS.docx.

Following the parsing, the terms in each query dictionary are then used to compute their cosine
scores. Each term is processed to find its weights (which does tf logarithm calculation * inverse
document frequency - idf) and then normalizing the resultant weights with the sqrt(sum of
weights^2). Next, each query-term-weight then retrieves the document weights of all postings where
the term exists in the document, and sums the multiplication of query weight with document weight.
Moreover, in this step we also use the document importance (H, M, L) to add more weight to more
important documents. We do so by retrieving its importance label, and apply a multiplication of 10,
8.5, and 1 respectively. This pushes the score of more important court documents while lowering
unimportant ones, giving us the final cosine score. We have omitted the normalization step, as
interestingly our system seems to perform better without it.

After which, the results are sorted in descending order of their final cosine score and based on
their zone (i.e., "TITLE" or "CONTENT"), where we gave a higher weight to "CONTENT" (80%) as
compared to "TITLE" (20%) based on our testing.

Finally, we write our rankings to the output file.


== Files included with this submission ==

- algorithm.py   : Code implementation for TopK class
- index.py       : Code implementation for indexing a directory to dictionary and posting files
- models.py      : Code implementation for VectorSpaceModel class
- query.py       : Code implementation for abstraction of query format and query expansion
- search.py      : Code implementation for executing search
- weighting.py   : Code implementation for TermFrequency, DocumentFrequency, TfIdfWeight class
- dictionary.txt : Encoded data file containing the dictionary that maps to the metadata of the
                   postings
- postings.txt   : Encoded data file containing all posting lists of legal data set
- bonus/         : Folder that contains code implementation for other query refinements tried, but
                   not included in submission
- BONUS.docx     : Explanation of the bonus component.
- README.txt     : This file

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0188493L-A0218271J-A0200025H-A0206154N, certify that we have followed the CS 3245
Information Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] We, A0188493L-A0218271J-A0200025H-A0206154N, did not follow the class rules regarding homework
assignment, because of the following reason:

-

We suggest that we should be graded as follows:

-

== References ==

- Chinese Unicode: https://unicode-table.com/en/blocks/
