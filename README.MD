pa1: Eliza
--------------------------------------------------------------

Eliza is a chatbot intended to simulate a conversation
with a therapist. It searches for defined language
patterns in the user's input, and attempts to give a
plausible response.

Example input and output:
<User> I want to rule the world.
[Eliza] User, why do you want to rule the world?
<User> I don't know, I think I crave power.
[Eliza] Why don't you tell me more about your cravings.

pa2: N-Gram Language Model
--------------------------------------------------------------

ngram.py is a program that learns an N-gram language model from an arbitrary number of plain text files
supplied by the user, whose filenames are passed in as command line arguments. To run this program,
place plain text files from which the program will learn the n-gram language model in the same directory
as ngram.py. To run it, type the following into the command line:
ngram.py n m filename1.txt filename2.txt [...]
n denotes the number of previous words taken into consideration when generating the next word. Enter a positive
integer for this value. The greater n is, the more comprehensible the generated sentences will be.
m is the number of sentences you want generated by the program. Enter a positive integer.
You must supply at least one plain text file for this program to work. Valid plain text files include those
available on the Project Gutenberg website (http://www.gutenberg.org). List the filenames as they appear downloaded
into the same directory in which ngram.py is located.
Sample run using  "Crime and Punishment," "War and Peace," and "Anna Karenina" from Project Gutenberg:
%python ngram.py 5 10 pg2554.txt pg2600.txt pg1399.txt

For more details, please refer to the comments at the beginning of ngram.py

pa3: POS Tagging
--------------------------------------------------------------

tagger.py is a program that takes as input a training file containing part of speech tagged text, and  a file
containing text to be part of speech tagged. This program uses the training data to determine the most likely
tag for each word in the text to be tagged.

For more details, please refer to the comments at the beginning of tagger.py

To run this program, place the training and test files into the same directory as pagger.py,
and enter the following into the command line:
python tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt
Replace "pos-train.txt" with the name of the training file, "pos-test.txt" with the name of the test file,
and "pos-test-with-tags.txt" with your desired output file name. If no arguments are entered after pos-train.txt and
pos-test.txt, then the name of the output file will default to "pos-test-with-tags.txt."

scorer.py is a program that accompanies tagger.py, a program that POS-tags a user-specified file with training data.
This program compares the output file generated by tagger.py against a key and calculates the accuracy of tagger.py.
In addition, it also generates a confusion matrix.

pa4: Word Sense Disambiguation
--------------------------------------------------------------

wsd.py is a program that takes as input a training file containing the word the user seeks to disambiguate used
in context that is tagged with the word sense. This is done based on the research of David Yarowsky, who
created a decision list algorithm designed to automatically restore the accent marks of Spanish and French words.
Since the restoration of accent marks was done based on context, the same logic could be applied for words
that are spelled the same, but with different meanings. Examples include the word bat, which can refer to a
specific type of flying rodent or a blunt instrument; or well, which can mean "good" or refer to a source of water.
Though this program is designed to work with any word given properly formatted training and test data, it was
tested on the word "line," which in the training and test data meant either a product line or a telephone line.
The program outputs the tagged test file as a plain text file whose filename is determined by command line arguments.

For more details, please refer to the comments at the beginning of wsd.py

To run this program, place the training and test files into the same directory as wsd.py,
and enter the following into the command line:
python wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt
Replace "line-train.txt" with the name of the training file, "line-test.txt" with the name of the test file,
"my-model.txt" with the desired name of the log file outputted by this program, and "my-line-answers.txt" with your
desired output file name. Ensure trainer and test files are placed in the same directory as wsd.py.
If no arguments are entered after line-train.txt and line-test.txt, then the name of the log and output files will
default respectively to "my-model.txt.txt" and "my-line-answers.txt."

scorer.py is a program that accompanies wsd.py, a program that takes as input a training file containing the word the
user seeks to disambiguate used in context that is tagged with the word sense.
This program compares the output file generated by wsd.py against a key and calculates the accuracy of wsd.py.
In addition, it also generates a confusion matrix.
Scorer program should be run as follows:
python3 scorer.py my-line-answers.txt line-key.txt
replace my-line-answers.txt with the name of the output text file from wsd.py and line-key.txt with the
name of the answer key file. Both should be in the same directory as scorer.py

pa5: Sentiment Analysis
--------------------------------------------------------------

sentiment.py is a program that takes as input a training file containing tweets with sentiment tags (positive or
negative). These tweets are cleaned and normalized - words that typically do not contribute to the meaning of the
overall phrase are removed, while certain features such as emoticons and hyperlinks are replaced with relevant tags.

For more details, please refer to the comments at the beginning of sentiment.py

To run this program, place the training and test files into the same directory as sentiment.py,
and enter the following into the command line:
python sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt
Replace "sentiment-train.txt" with the name of the training file, "sentiment-test.txt" with the name of the test file,
"my-model.txt" with the desired name of the log file outputted by this program, and "my-sentiment-answers.txt" with your
desired output file name. Ensure trainer and test files are placed in the same directory as sentiment.py.
If no arguments are entered after sentiment-train.txt and sentiment-test.txt, then the name of the log and output files
will default respectively to "my-model.txt.txt" and "my-sentiment-answers.txt."

scorer.py is a program that accompanies sentiment.py, a program that takes as input a training file containing tweets
tagged with their respective sentiments, which are either positive or negative.
This program compares the output file generated by sentiment.py against a key, calculating the accuracy of the program.
In addition, it also generates a confusion matrix.
Scorer program should be run as follows:
python3 scorer.py my-sentiment-answers.txt sentiment-key.txt
replace my-sentiment-answers.txt with the name of the output text file from sentiment.py and sentiment-key.txt with the
name of the answer key file. Both should be in the same directory as sentiment.py
