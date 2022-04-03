import math
import pickle
from weighting import TermFrequency, DocumentFrequency, TfIdfWeight
from collections import defaultdict
from algorithm import TopK

class VectorSpaceModel:
    def __init__(self, dict_file, posting_file):
        """
        Initializes VectorSpaceModel object.
        Loads dictionary file and posting file.
        Stores dictionary of terms and dictionary of weights.
        Args:
            dict_file    (str): File path of input dictionary file
            posting_file (str): File path of input posting file
        """
        with open(dict_file, 'rb') as f:
            self.dictionary, self.document_weights = pickle.load(f)
        
        self.posting_file = open(posting_file, 'rb')
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
            posting_list (list): List of documentId-frequency pairs
        """
        if term not in self.dictionary:
            return []

        _, pos, size = self.dictionary[term]

        self.posting_file.seek(pos)
        posting_list = pickle.loads(self.posting_file.read(size))
        
        return posting_list

    def cosine_score(self, query_detail, k): 
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
        query_vectors = defaultdict(float)
        length_norm = 0
        for query_term, query_term_freq in query_detail.items():
            if query_term not in self.dictionary:
                continue
            wtq = self.query_tf_idf.weight(query_term_freq, N, self.get_doc_freq(query_term))
            query_vectors[query_term] = wtq
            length_norm += wtq * wtq
        
        # Normalize cosine score
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
            for doc_id, _ in posting_list.items():
                wtd = self.document_weights[doc_id][query_term]
                score = wtq * wtd
                scores[doc_id] += score

        top_k = TopK(k)
        for doc_id, score in scores.items():
            top_k.add((score, doc_id))
        
        return top_k.result()
