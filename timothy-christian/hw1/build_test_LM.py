#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt
import math

from collections import defaultdict, Counter

class LanguageModel:
    """
    alien_threshold - the smallest ratio of ngrams recognised to the ngrams in the sentence that we can 
        tolerate. A sentence is identified as 'other' if it is lower than this threshold.
    """
    alien_threshold = 0.55

    def __init__(self, lang_to_sentences, n=4):
        """
        Initialises the Language Model by first building a count model, and then smoothing it.
        The probabilistic model is then computed.

        Args:
            lang_to_sentences: A dictionary of type str (lang) -> list (of string sentences)
            n: The value of n for the ngram model. Defaults to 4
        """
        self.n = n
        count_models = self.build_models(lang_to_sentences)
        count_models = self.add_one_smoothing(count_models)
        self.models = self.convert_to_prob_model(count_models)
    
    def convert_to_prob_model(self, count_models):
        """
        Converts given count_models into a model that uses probability

        Returns:
            models: A dictionary of type str (lang) -> (dict: str (ngram) -> float (prob)).
        """

        ngram_counts = Counter()
        for lang, model in count_models.items():
            count = sum(model.values())
            ngram_counts[lang] = count
        
        models = defaultdict(lambda: defaultdict(float))
        for lang, count_model in count_models.items():
            denom = ngram_counts[lang]
            for ngram, count in count_model.items():
                models[lang][ngram] = count / denom
            
        return models
    
    def build_models(self, lang_to_sentences):
        """
        Builds an ngram language model.
        Args:
            lang_to_sentences: A dictionary of type str (lang) -> list (of string sentences)
        
        Returns:
            count_models: A dictionary of type str (lang) -> Counter. The Counter counts the occurrence of the ngram string
        """
        count_models = defaultdict(Counter)
        def add_sentence_to_model(sentence, model):
            """
            A helper function that abstracts the behaviour of adding a particular sentence to the model
            """
            n = self.n
            for i in range(len(sentence)-n+1):
                ngram = sentence[i:i+n]
                model[ngram] += 1


        for lang, sentences in lang_to_sentences.items():
            model = count_models[lang]
            for sentence in sentences:
                add_sentence_to_model(sentence, model)
        
        return count_models

    def add_one_smoothing(self, count_models):
        """
        Performs add-one smoothing to the model.

        Args:
            models: A dictionary of type str (lang) -> Counter. The Counter counts the occurrence of the ngram string
        
        Returns:
            models: A dictionary of type str (lang) -> Counter. The Counter counts the occurrence of the ngram string after smoothing.
        """

        # Collect all the ngrams observed from the training set, regardless of which lang it belongs to
        allngrams = set().union(*count_models.values())
        for ngram in allngrams:
            for model in count_models.values():
                model[ngram] += 1
        
        return count_models
    
    def predict(self, sentence):
        """
        Predicts which language the model belong to.

        Args:
            sentence: A str of the sentence we are predicting

        Returns:
            The prediction based on the information from the training set.
        """
        n = self.n
        results = {}
        for lang, model in self.models.items():
            probs = []
            for i in range(len(sentence)-n+1):
                ngram = sentence[i:i+n]
                if model[ngram] == 0:
                    # assignment says to ignore the ngram if not found
                    continue
                    
                probs.append(model[ngram])
            
            # observation: `len(probs)` is the same for all languages, due to the add-one smoothing
            # if this does not hold, we should NOT return immediately, but rather check if all languages
            # report 'other'

            # numerator is the number of recognised ngrams, and denominator is the number of ngrams for the sentence
            ratio_recognised = len(probs) / (len(sentence)-n+1)
            # print(ratio_recognised)
            if ratio_recognised <= self.alien_threshold:
                return "other"

            # log(pr1 * pr2) = log(pr1) + log(pr2)
            # if x > y => log(x) > log(y)
            logprob = sum([math.log10(prob) for prob in probs])

            # probably not good for tiebreaking, but if a tie happens, we have to decide on one either way.
            results[logprob] = lang

        max_logprob = max(results.keys())
        return results[max_logprob]
        

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    lang_to_sentences = defaultdict(list)
    with open(in_file, 'r') as f:
        for line in f:
            lang, sentence = line.strip().split(" ", 1)
            lang_to_sentences[lang].append(sentence)

    return LanguageModel(lang_to_sentences, n=4)


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    results = []
    with open(in_file, 'r') as f:
        for line in f:
            line = line.strip()
            result = (LM.predict(line), line)
            results.append(result)
    
    with open(out_file, 'w') as f:
        for lang, sentence in results:
            f.write(f"{lang} {sentence}\n")


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
