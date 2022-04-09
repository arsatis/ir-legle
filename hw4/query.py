from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

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

        # Stemming + Case-folding
        ps = PorterStemmer()
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
            tokens[i] = ps.stem(tokens[i])

        print("tokens: ", tokens)

        # TODO : Handle relevant_docs to do pseudo Relevant Feedback
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
