This is the README file for A0188493L's submission

== Python Version ==

I'm using Python Version 3.8.3 for this assignment.

== General Notes about this assignment ==

The high level idea is to create a class `LanguageModel`. It takes in a dictionary with language 
as key and the list of sentences as values.

-- Model-building --
The first step would be to build an initial model for each of the language, by iterating
through the 4-grams of each sentence. 

In this program, special START and END tokens are NOT considered.

Next, add-one smoothing is performed. The smoothing is done only using the known ngrams in the model. 
Then, the probability of occurrence inside the model is computed.

-- Prediction --
During the prediction phase, for every language we have in our model, we will iterate through the ngram
of the input sentence. A key code here is to skip the ngram if it has not been seen in the model, based on
the instructions of the assignment. If it is found, we append the value to a list of probabilities.

Instead of multiplying the probabilities directly, what we do here is to take the logarithm of probabilities and summing them.

That is instead of doing Pr[A] * Pr[B], we do log(Pr[A] * Pr[B]) = log(Pr[A]) + log(Pr[B])

We do this because multiplying probabilities result in a value that is so small it effectively becomes 0. This approach
of taking logarithm works due to the monotocity of logarithms. To be precise, if x >= y, this implies that log(x) >= log(y).
Hence, taking maximum of the value would correspond to the result that has maximum probability.

-- Outputting 'others' --
To output 'others', the strategy taken is to measure what percentage of the sentence's ngram is not found in the model.
This is a reasonable measure because if a language is an alien language, it should be 'far' enough from the languages
that we are trained in. As a result, this implies that we might not have seen enough of such ngrams to be confident this belongs
to a certain language.

Inside the loop, we take this percentage by considering the length of numerators, and divided by the number of ngrams in the program.
If it falls below a certain threshold, then we output 'others', because that means the percentage of known ngrams in this
sentence is too low.

A potential question might be, what if one of the language models that have not been checked will not return 'others'? i.e. for that
language, we see the ratio above the threshold. For the context of this assignment, it is not possible due to the add-one smoothing
performed. Because of the smoothing, all language models will have the same known ngrams, making it sufficient to check just for one.

The threshold chosen is 0.55, which is due to empirical measurements. I have tested my model on several texts of 
different languages (Japanese, English, Alien, Spanish, German, Indonesian, Malaysian). For the non-known languages,
I observe that around 20-50% of the ngrams are known, in this model, occasionally exceeding the 50% threshold. Thus
0.55 is chosen, and this makes sense as 0.5 represents a coin flip. So we should be significantly more sure than a coin
flip that a sentence is part of a language.

== Files included with this submission ==

The languages/ folder contain my personal test files that I used to verify correctness
of my Indo/Malay detector, and the other languages are to measure the threshold for 'others'.

Tamil is not tested as I am unsure of the language to verify that it is indeed Tamil.

README.txt - this file!
build_test_LM.py - implementation code
eval.py - unchanged
input.test.txt - unchanged
input.train.txt - unchanged
input.correct.txt - unchagned
languages/indo.test.txt
languages/japanese.test.txt
languages/malay.test.txt
languages/spanish.test.txt
languages/german.test.txt
languages/english.test.txt
languages/alien.test.txt

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0188493L, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

NLTK Documentation, whose `logprob` methods gave me the inspiration
for adding up logarithm of probabilities