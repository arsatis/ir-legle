from collections import Counter
from nltk.stem import PorterStemmer
from nltk import word_tokenize

class FreeTextParser:
    """
    Parsers free text queries.
    """
    def __init__(self):
        self.stemmer = PorterStemmer()

    def to_query_detail(self, query):
        """
        Converts free text query into query details
        Args:
            query (str): Target free text query
        Returns:
            query_detail (dict): Dictionary of query terms and frequency
        """
        query_detail = Counter()
        cleaned_query = query.strip()
        for unstemmed_word in word_tokenize(cleaned_query):
            if unstemmed_word == '': # extra whitespaces
                continue

            term = self.stemmer.stem(unstemmed_word.lower())
            query_detail[term] += 1

        return query_detail