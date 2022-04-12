from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter

class QueryDetails:
    """
    Does pre-processing, determines type of query, and put the respective information
    into variables.

    Args:
        query           (str)         : String form of the whole query
        relevant_docs   (list[int])   : List of all the given relevant doc_ids

    Variables:
        relevant_docs   (list[int])   : List of all the given relevant doc_ids 
        type            (str)         : The type of query which is either free-text / boolean / boolean with phrasal / phrasal
        terms           (list[str])   : All of the query terms, where phrasal queries will be in a nested list
        counts          (Counter[str]): The frequency of each terms
    """
    def __init__(self, query, relevant_docs):
        self.type = "free-text"
        self.terms = []

        # Word_tokenization
        tokens = word_tokenize(query)

        # Check if it's a boolean query
        AND_indexes = []
        for i in range(len(tokens)):
            if tokens[i] == "AND":
                self.type = "boolean"
                AND_indexes.append(i)

        # Error-checking: Check for proper usage of AND
        if len(AND_indexes) > 0:
            for i in range(len(AND_indexes) - 1):
                if AND_indexes[i + 1] - AND_indexes[i] == 1:
                    raise Exception("Boolean query: You can't have consecutive ANDs")
            if AND_indexes[-1] == len(tokens) - 1 or AND_indexes[0] == 0:
                raise Exception("Boolean Query: You can't have AND as the first / last term!")

        # Stemming + Case-folding
        ps = PorterStemmer()
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
            tokens[i] = ps.stem(tokens[i])

        print("tokens: ", tokens)

        # TODO : Handle relevant_docs to check against pseudo Relevant Feedback
        self.relevant_docs = relevant_docs
        
        # Check for quotations for phrasal queries
        phrasal_start_index = -1
        phrasal_end_index = -1
        for i in range(len(tokens)):
            if tokens[i] == "``": # start quotation
                if self.type == "boolean":
                    self.type = "boolean with phrasal"
                elif self.type == "free-text":
                    self.type = "phrasal"
                phrasal_start_index = i 
            elif tokens[i] == "''": # end quotation
                phrasal_end_index = i
                self.terms.append(tokens[phrasal_start_index + 1 : phrasal_end_index])
                # reset the start and end index to check for more phrasal queries
                phrasal_start_index = -1
                phrasal_end_index = -1
            elif phrasal_start_index == -1 and phrasal_end_index == -1 and i not in AND_indexes:
                self.terms.append(tokens[i])

        if self.type == "free-text":
            self.terms = tokens
        
        self.counts = Counter(self.terms)

class QueryRefiner:
    # TODO: Docs

    def __init__(self, query_details):
        self.query_details = query_details
    
    def pseudo_relevance_feedback(self, doc_ids):
        # TODO: Implement such that it mutates query_details with an updated .counts property
        pass

    def query_expansion(self):
        # TODO: If we decide to implement this
        pass
    
    def get_current_refined(self):
        return self.query_details
