import math
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
            term (str): Target term
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
            term (str): Target term
        Returns:
            posting_list (list): List of documentId - list of positions pairs
        """
        if term not in self.dictionary:
            return []

        _, pos, size = self.dictionary[term]

        self.posting_file.seek(pos)
        posting_list = pickle.loads(self.posting_file.read(size))
        
        return posting_list

    def get_document_weight(self, tf):
        """
        TODO: documentation
        """
        return 1 + math.log10(tf) if tf >= 1 else 0

    def cosine_score(self, query, k): 
        """
        Computes the cosine score and returns the top k (score, doc_id) pairs
        Args:
            query_detail (dict): Dictionary of query terms and frequency
            k (int): Top number of results to return
        Returns:
            Descending list of score-documentId pairs (by score)
        """
        N = len(self.document_weights)
        scores = defaultdict(float)
        
        # Calculate cosine score
        query_detail = Counter(query.terms)
        query_vectors = defaultdict(float)
        length_norm = 0
        for query_term, query_term_freq in query_detail.items():
            if query_term not in self.dictionary:
                continue
            wtq = self.query_tf_idf.weight(query_term_freq, N, self.get_doc_freq(query_term))
            query_vectors[query_term] = wtq
            length_norm += wtq * wtq
        
        # Normalize cosine score (TODO: fix this? iirc Christian mentioned that their method skipped some computation)
        if length_norm > 0:
            length_norm = math.sqrt(length_norm)
            for query_term, _ in query_detail.items():
                query_vectors[query_term] /= length_norm

        # Calculate final score w/ doc weight
        for query_term, query_term_freq in query_detail.items():
            if query_term not in self.dictionary:
                continue
                
            wtq = query_vectors[query_term]
            posting_list = self.get_posting_list(query_term)
            for doc_id, pos in posting_list[1]:
                tf = len(pos)
                wtd = self.doc_tf_idf.weight(tf)
                score = wtq * wtd
                scores[doc_id] += score

        # find top k results
        top_k = TopK(k)
        for doc_id, score in scores.items():
            top_k.add((score, doc_id))
        
        return top_k.result()