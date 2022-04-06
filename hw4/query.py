from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

class QueryDetails:
    """
    Does pre-processing, determines type of query, and put the respective information
    into variables.

    Args:
        query         (str)  : String form of the whole query
        relevant_docs (list) : List of all the given relevant doc_ids

    Variables:
        type                : the type of querym which is either a boolean or free-text
        terms (free-text)   : all the terms in the free-text query
        lhs (boolean query) : term on the LHS of the AND query
        rhs (boolean query) : term on the RHS of the AND query
        relevant_docs       : List of all the given relevant doc_ids 
    """
    def __init__(self, query, relevant_docs):
        self.type = "free-text"

        # Word_tokenization
        tokens = word_tokenize(query)

        # Check if it's a boolean query
        for i in range(len(tokens)):
            if tokens[i] == "AND":
                self.type = "boolean"
                booleanIndex = i
                break

        # Stemming + Case-folding
        ps = PorterStemmer()
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
            tokens[i] = ps.stem(tokens[i])

        print("tokens: ", tokens)

        # TODO : Handle relevant_docs to do pseudo Relevant Feedback
        self.relevant_docs = relevant_docs
        
        # Check for quotations for phrasal queries
        phrasal_query = []
        phrasal_start_index = -1
        phrasal_end_index = -1
        for i in range(len(tokens)):
            if tokens[i] == "``" and phrasal_start_index == -1: # start quotation
                phrasal_start_index = i + 1
            elif tokens[i] == "''" and phrasal_end_index == -1: # end quotation
                phrasal_end_index = i
                phrasal_query = tokens[phrasal_start_index : phrasal_end_index]
                break
                
        if self.type == "free-text":
            self.terms = tokens
        else:
            # check if there's phrasal_query, and on which side
            #? Edge case: 2 phrasal queries -> "apple bottom" AND "hello world" <- is this possible?
            if phrasal_start_index != -1:
                if phrasal_start_index == 1:
                    self.lhs = phrasal_query
                    self.rhs = tokens[booleanIndex + 1: len(tokens)]
                elif phrasal_start_index > booleanIndex:
                    self.rhs = phrasal_query
                    self.lhs = tokens[0: booleanIndex]
            else:
                self.lhs = tokens[0: booleanIndex]
                self.rhs = tokens[booleanIndex + 1: len(tokens)]
