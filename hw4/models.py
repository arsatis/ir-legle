import pickle
from weighting import TermFrequency, DocumentFrequency, TfIdfWeight
from collections import defaultdict, Counter
from algorithm import TopK

class VectorSpaceModel:
    def __init__(self, dictionary, document_weights, postings):
        """
        Initializes VectorSpaceModel object.
        Loads dictionary file and posting file.
        Stores dictionary of terms and dictionary of weights.
        Args:
            dict_file    (str): File path of input dictionary file
            posting_file (str): File path of input posting file
        """
        self.dictionary = dictionary
        self.document_weights = document_weights
        self.posting_file = postings

        self.query_tf_idf = TfIdfWeight(TermFrequency.LOGARITHM, DocumentFrequency.IDF)
        self.doc_tf_idf = TfIdfWeight(TermFrequency.LOGARITHM, DocumentFrequency.NO)
    
    def get_doc_freq(self, term):
        """
        Retrieves frequency of term
        Args:
            term     (str): Target term
        Returns:
            doc_freq (int): Number of documents that contain the term
        """
        if term not in self.dictionary:
            return 0
        
        doc_freq, _, _ = self.dictionary[term]
        return doc_freq    

    def get_posting_list(self, term):
        """
        Retrieves posting list of term from posting file
        Args:
            term          (str): Target term
        Returns:
            posting_list (list): List of documentId - list of positions pairs
        """
        if term not in self.dictionary:
            return []

        _, pos, size = self.dictionary[term]

        self.posting_file.seek(pos)
        posting_list = pickle.loads(self.posting_file.read(size))
        
        return posting_list

    def get_document_weight(self, doc_id):
        """
        Returns the document weight of document with the given id.
        Args:
            doc_id (str): Target document id
        Returns:
            (float): Weight of the target document
        """
        # we should only be calling this function on weights that we know exist
        assert doc_id in self.document_weights

        return self.document_weights[doc_id][0]

    def get_document_importance(self, doc_id, get_vals=False):
        """
        Returns the weight of the document based on their court importance. (H, M, L)
        Args:
            doc_id       (str): Target document id
            get_vals (boolean): True if return value should an float/score, false if the return value should be a str indicating the importance
        Returns:
            (float): Multiplier of court importance
        """
        # we should only be calling this function on weights that we know exist
        assert doc_id in self.document_weights

        if not get_vals:
            return self.document_weights[doc_id][1]

        if self.document_weights[doc_id][1] == 'H':
            return 10
        elif self.document_weights[doc_id][1] == 'M':
            return 8.5
        elif self.document_weights[doc_id][1] == 'L':
            return 1
        else:
            return 0

    def cosine_score(self, query, k = None): 
        """
        Computes the cosine score and returns the top k (score, doc_id) pairs
        Args:
            query_detail (dict): Dictionary of query terms and frequency
            k             (int): Top number of results to return
        Returns:
            (list): Descending list of score-documentId pairs by score
        """
        N = len(self.document_weights)
        scores = defaultdict(float)
        
        # Calculate cosine score
        query_freq = Counter(query.terms)
        query_vectors = defaultdict(float)
        
        for query_term, query_term_freq in query_freq.items():
            if query_term not in self.dictionary:
                continue
            wtq = self.query_tf_idf.weight(query_term_freq, N, self.get_doc_freq(query_term))
            query_vectors[query_term] = wtq

        # Calculate final score w/ doc weight. Lines 3-6 in lect algo
        for query_term, query_term_freq in query_freq.items():
            if query_term not in self.dictionary:
                continue
                
            wtq = query_vectors[query_term]
            posting_list = self.get_posting_list(query_term)
            for doc_id, pos in posting_list[1]:
                tf = len(pos)
                wtd = self.doc_tf_idf.weight(tf)
                score = wtq * wtd
                scores[doc_id] += score
        
        # Normalisation step. Line 8-9 of the lect algo
        # for doc_id, score in scores.items():
        #     scores[doc_id] = score / self.get_document_weight(doc_id)

        if k == None:
            # does the same thing as .result() in top_k
            return reversed(sorted([(score * self.get_document_importance(doc_id, get_vals=True), doc_id) for doc_id, score in scores.items()]))

        # find top k results
        top_k = TopK(k)
        for doc_id, score in scores.items():
            top_k.add((score * self.get_document_importance(doc_id, get_vals=True), doc_id))
        
        return top_k.result()
