from nltk.stem import PorterStemmer

class Tokeniser:
    # ===== HELPER =====
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    OPEN_PAREN = '('
    CLOSE_PAREN = ')'
    binary_ops = set(['AND', 'OR'])
    unary_prefix_ops = set(['NOT'])
    precedence = {
        'NOT': 90,
        'AND': 80,
        'OR': 70,
    }

    @staticmethod
    def is_open_paren(token):
        return token == '('

    @staticmethod
    def is_close_paren(token):
        return token == ')'

    @staticmethod
    def is_paren(token):
        """
        Returns true if token is open parenthesis or close parenthesis.
        """
        return Tokeniser.is_open_paren(token) or Tokeniser.is_close_paren(token)

    @staticmethod
    def is_binary_op(token):
        """
        Returns true if token is AND or OR.
        """
        return token in Tokeniser.binary_ops

    @staticmethod
    def is_unary_prefix_op(token):
        """
        Returns true if token is NOT.
        """
        return token in Tokeniser.unary_prefix_ops

    @staticmethod
    def is_op(token):
        """
        Returns true if token is an operator (binary or unary).
        """
        return Tokeniser.is_binary_op(token) or Tokeniser.is_unary_prefix_op(token)

    @staticmethod
    def is_value(token):
        """
        Returns true if token is not an operator or a parenthesis.
        """
        return not (Tokeniser.is_op(token) or Tokeniser.is_paren(token))
    # ===================

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.tokens  = []
        
    def add_token(self, token):
        """
        Adds token into list of tokens. Stems token if it is a query term, not an operator.
        Args:
            token (str): A word or term to be tokenised
        """
        if Tokeniser.is_op(token):
            self.tokens.append(token)
        else:
            self.tokens.append(self.stemmer.stem(token.lower()))

    def tokenise(self, query):
        """
        Splits query into a list of tokens.
        Args:
            query (str): A boolean query to be tokenised
        Returns:
            tokens (list): List of tokens (query terms, operators, and parenthesis)
        """
        self.tokens = []
        uncleaned_words = query.strip().split(" ")
        for word in uncleaned_words:
            if word == '': # handle extra whitespaces
                continue 

            if Tokeniser.is_open_paren(word[0]):
                self.tokens.append(Tokeniser.OPEN_PAREN)
                self.add_token(word[1:])
            elif Tokeniser.is_close_paren(word[-1]):
                self.add_token(word[:-1])
                self.tokens.append(Tokeniser.CLOSE_PAREN)
            else:
                self.add_token(word)
        
        return self.tokens

