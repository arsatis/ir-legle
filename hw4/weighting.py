# ported over from T-C
import math

class TermFrequency:
    LOGARITHM = 0

    @staticmethod
    def logarithm(term_freq):
        """
        Calculates logarithm frequency
        Args:
            term_freq (int): Frequency of term in the document
        """
        if term_freq <= 0:
            return 0
        
        return 1 + math.log10(term_freq)

    @staticmethod
    def weight(setting, term_freq):
        """
        Calculates term frequency weight
        Args:
            setting (int): Type of term frequency calculation
            term_freq (int): Frequency of term in the document
        """
        if setting == TermFrequency.LOGARITHM:
            return TermFrequency.logarithm(term_freq)
        else:
            raise Exception(f"Unknown setting: {setting}")

class DocumentFrequency:
    NO = 0
    IDF = 1

    @staticmethod
    def no():
        return 1

    @staticmethod
    def idf(N, doc_freq):
        """
        Calculates idf
        Args:
            N (int): The size of the collection
            doc_freq (int): Number of documents that contain the term
        """
        assert doc_freq <= N
        if doc_freq == 0:
            return 0

        return math.log10(N/doc_freq)
    
    @staticmethod
    def weight(setting, N=1, doc_freq=1):
        """
        Calculates document frequency weight
        Args:
            setting (int): Type of document frequency calculation
            N (int): The size of the collection
            doc_freq (int): Number of documents that contain the term
        """
        if setting == DocumentFrequency.NO:
            return DocumentFrequency.no()
        elif setting == DocumentFrequency.IDF:
            return DocumentFrequency.idf(N, doc_freq)
        else:
            raise Exception(f"Unknown setting: {setting}")

class TfIdfWeight:
    def __init__(self, tf_setting, df_setting):
        """
        Initializes weight calculator
        Args:
            tf_setting (int): Type of term frequency calculation
            df_setting (int): Type of document frequency calculation
        """
        self.tf_setting = tf_setting
        self.df_setting = df_setting
    
    def weight(self, term_freq, N=1, doc_freq=1):
        """
        Calculates weight using term frequency and document frequency
        Args:
            term_freq (int): Frequency of term
            N (int): Total frequency of all terms
            doc_freq (int): Frequency of document
        """
        return (TermFrequency.weight(self.tf_setting, term_freq) *
            DocumentFrequency.weight(self.df_setting, N, doc_freq))
