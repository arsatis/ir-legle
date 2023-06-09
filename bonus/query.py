from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet as wn
from collections import Counter
import nltk

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
        raw_tokens      (list[str])   : List of the raw tokens before stemming and case-folding
    """
    def __init__(self, query, relevant_docs):
        self.type = "free-text"
        self.terms = []
        self.extraterms = {} # used for rocchio
        self.num_normalising_docs = 1
        self.alpha = 1

        # Word_tokenization
        tokens = word_tokenize(query)
        self.raw_tokens = tokens[:]

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
                    self.type = "invalid"
            if AND_indexes[-1] == len(tokens) - 1 or AND_indexes[0] == 0:
                self.type = "invalid"

        # Lemmatization (to verb form) + Case-folding
        # lemmatizer = WordNetLemmatizer()
        stemmer = PorterStemmer()
        expander = WordnetExpander()
        new_tokens = []
        for term, tag in nltk.pos_tag(tokens):
            tag = expander.get_wordnet_pos(tag)
            term = stemmer.stem(term.lower())
            # term = lemmatizer.lemmatize(term.lower(), pos=tag if tag else wn.VERB) # because lemmatizer cannot parse empty string as pos
            new_tokens.append(term)
        tokens = new_tokens

        print("tokens: ", tokens)

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
    
    @property
    def count(self):
        d = dict(Counter(self.terms))
        for term in d:
            d[term] *= self.alpha

        beta = (1 - self.alpha)

        # the logic for Rocchio algorithm (if it exists)
        for term, freq in self.extraterms.items():
            val = beta * (freq / self.num_normalising_docs)
            if term in d:
                d[term] += val
            else:
                d[term] = val
        return d
    
    def to_free_text(self):
        """
        Converts query from a boolean type to a free text type
        """
        def valid_raw_token(term):
            invalid_tokens = ["''", "``", "AND"]
            return term in invalid_tokens

        if self.type == "free-text":
            return

        flattened_terms = []
        for term in self.terms:
            if isinstance(term, str):
                flattened_terms.append(term)
            else: # assume it's array
                flattened_terms.extend(term)

        self.terms = flattened_terms
        self.raw_tokens = [term for term in self.raw_tokens if (not valid_raw_token(term))]
        self.type = "free-text"
        

class QueryRefiner:
    # TODO: Docs

    def __init__(self, query_details):
        self.query_details = query_details
    
    def pseudo_relevance_feedback(self, prf_terms):
        # gets the top k documents' most important terms and simply append it
        new_terms = self.query_details.raw_tokens + prf_terms
        new_query = " ".join(new_terms)

        self.query_details = QueryDetails(new_query, self.query_details.relevant_docs)
    
    def pseudo_rocchio(self, prf_terms, N):
        # not exactly rocchio, but similar. All the bulk of the calculation is inside count() method of QueryDetails
        # similar to pseudo_relevance_feedback but the difference is we take "average"

        self.query_details.num_normalising_docs = N
        self.query_details.extraterms = dict(Counter(prf_terms))
        self.alpha = 0.8

    def query_expansion(self, new_synonyms_per_term=0):
        expander = WordnetExpander()
        terms = self.query_details.raw_tokens
        additional_terms = expander.get_synonyms_of(terms, new_synonyms_per_term)
        
        print(f"terms in query expansion: {terms}")
        print(f"additional terms: {additional_terms}")
        new_terms = terms + additional_terms
        new_query = " ".join(new_terms)
        self.query_details = QueryDetails(new_query, self.query_details.relevant_docs)
    
    def get_current_refined(self):
        return self.query_details

CUSTOM_SYNONYMS = [
    set(['murder', 'kill', 'victim', 'harm', 'manslaughter']),
    set(['bail', 'ankle', 'electronic', 'monitoring', 'bond', 'exoneration', 'forfeiture', 'test', 'cost']),
    set(['knife', 'weapon', 'firearm', 'balaclava', 'ammunition', 'gun', 'machete', 'machine gun', 'rifle', 'shotgun', 'sword']),
    set(['arson', 'fire', 'burn', 'ignite', 'pyro', 'firebombing']),
    set(['robbery', 'burglary', 'steal', 'money', 'jewelry', 'rob', 'heist', 'mask']),
    set(['provoke', 'taunt', 'tempt', 'threaten']),
    set(['assist', 'acquaint', 'accomplice', 'partner', 'in', 'crime']),
    set(['acquittal', 'extradition', 'not guilty']),
    set(['scam', 'fool', 'fake', 'fraud', 'blackmail', 'deceit', 'deception', 'extortion', 'hoax', 'sham', 'ripoff', 'cheat']),
    set(['hate', 'crime', 'racist', 'black', 'asian', 'yellow', 'white', 'race', 'police brutality', 'unfair', 'biased']),
    set(['corruption', 'bribe', 'extort', 'nepotism', 'fraud', 'graft']),
    set(['scandal', 'misconduct', 'sex', 'grades', 'affair', 'gratification', 'explicitly']),
    set(['adult', 'mature', 'grownup', 'grown', 'of age', 'adolescent', 'infant', 'child', 'consent', '18', 'minor', 'legal', 'alcohol']),
    set(['kidnap', 'pay', 'phone', 'call', 'warehouse', 'abandon']),
    set(['drugs', 'death penalty', 'grams', 'medical marijuana', 'overdose', 'OD', 'drug cartel']),
    set(['arrest', 'capture', 'detention', 'prison', 'imprisonment', 'jail', 'incarceration', 'custody', 'stop', 'captivity']),
    set(['drink-driving', 'alcohol', 'influence', 'speeding', 'red-light', 'accident', 'incident', 'crash', 'totaled', 'car', 'negligent']),
    set(['rape', 'sex', 'intercourse', 'carnal knowledge', 'sexual assault', 'molest', 'violate', 'forced', 'penetration', 'penis', 'vagina']),
    set(['quiet', 'muted', 'silent', 'soft', 'hushed', 'low', 'mute']),
    set(['phone', 'telephone', 'call', 'ring', 'communicate', 'relay']),
    set(['prostitute', 'payment', 'gigolo', 'hooker', 'whore', 'call girl', 'degrade']),
    set(['damage', 'injury', 'burn', 'cripple', 'harm', 'hurt', 'impair', 'loss', 'ravage', 'ruin', 'scorch', 'tarnish', 'wound', 'wreck', 'rot', 'disfigure', 'deface', 'spoil']),
]

# if wanna be extensible, can make this implement an "interface"
# and then have different classes denoting different thesaurus implement that interface
# but it's not an SWE project so we keep it at this
class WordnetExpander:
    def get_synonyms_of(self, terms, k):
        """
        Args:
        terms (str): The original terms that appears in the queries
        k     (int): The number of synonyms to be taken per term
        """

        tagged_terms = nltk.pos_tag(terms)
        all_new_terms = []
        for term, tag in tagged_terms:
            # try custom synonyms first
            new_terms = self.get_custom_synonym(term, k)
            if not new_terms: # turns out custom synonym doesn't give us anything
                synsets = self.get_synsets(term, tag)
                new_terms = self.get_k_from_synsets(synsets, term, k)
            print(f"{term}: {new_terms}")
            all_new_terms.extend(new_terms)

        return all_new_terms
    
    def get_custom_synonym(self, term, k):
        new_terms = []
        for syns in CUSTOM_SYNONYMS:
            if term in syns:
                syns_copy = syns.copy()
                new_terms.extend(syns_copy)
        return new_terms
        
        # randomly draws k terms to be included in the expanded query
        # not used for now, code kept here just in case reversion is needed
        # new_terms = []
        # for syns in CUSTOM_SYNONYMS:
        #     if term in syns:
        #         syns_copy = syns.copy()
        #         syns_copy.remove(term) # don't want to use this term
        #         new_terms.extend(random.sample(syns_copy, k))
        
        # if len(new_terms) > k: # we only want k things
        #     new_terms = random.sample(new_terms, k)

        # return new_terms
    
    # extracted to a function because I needed to return from innermost loop to "break" out of two loops
    def get_k_from_synsets(self, synsets, term, k):
        """
        Returns a list of k synonyms extracted from synsets
        """
        def is_invalid_synonym(syn):
            return (syn == term 
                or syn in new_terms
                or not syn.isalnum()
                or syn == "AND") # edge case, we don't want free-text to become boolean query

        new_terms = set() # maxsize: k
        for synset in synsets:
            for syn in synset.lemma_names():
                if is_invalid_synonym(syn):
                    continue
                
                new_terms.add(syn)
                if len(new_terms) >= k:
                    return list(new_terms)
        
        return list(new_terms)

    
    def get_synsets(self, term, tag):
        """
        Get synsets in decreasing order of relevance.
        term (str): Original term.
        tag (str): Tag obtained from nltk.pos_tag
        """
        unsorted_synsets = wn.synsets(term, pos=self.get_wordnet_pos(tag))
        if not unsorted_synsets:
            # empty
            return unsorted_synsets
        
        # heuristic: choose the first one and score with respect to first synonym set
        # TODO: Experiment whether this is good or not
        base_synset = unsorted_synsets[0]
        score_synset_pairs = reversed(sorted([(base_synset.wup_similarity(synset), synset) for synset in unsorted_synsets]))

        return [synset for _, synset in score_synset_pairs]
        
    def get_wordnet_pos(self, treebank_tag):
        """
        Taken from https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python.
        Gets the part-of-speech tagging to correctly get synonym sets.
        """
        if treebank_tag.startswith('J'):
            return wn.ADJ
        elif treebank_tag.startswith('V'):
            return wn.VERB
        elif treebank_tag.startswith('N'):
            return wn.NOUN
        elif treebank_tag.startswith('R'):
            return wn.ADV
        else:
            return ''