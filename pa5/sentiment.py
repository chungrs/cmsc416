"""
Programming Assignment 5 - Sentiment Analysis

Roy Chung
20210420
CMSC 416-001

sentiment.py is a program that takes as input a training file containing tweets with sentiment tags (positive or
negative). These tweets are cleaned and normalized - words that typically do not contribute to the meaning of the
overall phrase are removed, while certain features such as emoticons and hyperlinks are replaced with relevant tags.

The following are the formulas used to calculate the probability that a tweet has a positive or negative sentiment:
The product of P(sentiment) and (P(word|sentiment) for all words in bag)

For numerical stability, the log version is used:
log(P(sentiment)) + summation of log(freq(word AND sentiment)/freq(sentiment)) for each word in bag.

Below is an example of how training data should be formatted:
<corpus lang="en">
<lexelt item="sentiment">
<instance id="620821002390339585">
<answer instance="620821002390339585" sentiment="negative"/>
<context>
Does @macleansmag still believe that Ms. Angela Merkel is the "real leader of the free world"?  http://t.co/isQfoIcod0 (Greeks may disagree
</context>
</instance>
<instance id="621090050848198657">
<answer instance="621090050848198657" sentiment="negative"/>
<context>
By Michael Nienaber BERLIN, July 10 (Reuters) - The parties in Angela Merkel's coalition government sent conflicting signals on the latest
</context>
</instance>
<instance id="641666486793203712">
<answer instance="641666486793203712" sentiment="positive"/>
<context>
That may just be the most shocking moment of todays #AppleEvent, @Microsoft doing a demo on the new #iPadPro.....
</context>
</instance>
</lexelt>
</corpus>

Test data is formatted similarly, but without <answer instance="########" sentiment="[sentiment]"/> tags

Results can be scored by comparing the output file to the key using the accompanying scorer.py.

The accuracy of my test run was: 67.24%, with the following confusion matrix:

Predicted Sentiment  negative  positive
Actual Sentiment
negative                   29        43
positive                   33       127

The most frequent sentiment baseline for this particular dataset was 68.67%
The most frequent sentiment was "positive" with a total number of 160 occurrences out of 233 instances.

To run this program, place the training and test files into the same directory as sentiment.py,
and enter the following into the command line:

python sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt
Replace "sentiment-train.txt" with the name of the training file, "sentiment-test.txt" with the name of the test file,
"my-model.txt" with the desired name of the log file outputted by this program, and "my-sentiment-answers.txt" with your
desired output file name. Ensure trainer and test files are placed in the same directory as sentiment.py.
If no arguments are entered after sentiment-train.txt and sentiment-test.txt, then the name of the log and output files
will default respectively to "my-model.txt.txt" and "my-sentiment-answers.txt."
"""

from collections import Counter
import re
from sys import argv
from math import log

# Global variables
wordsent_freq = Counter()
sent_freq = Counter()
train_data = dict()
model_filename = ""
output_filename = ""


# imports training and test data as a list of instances with all of the tags intact for further processing
def import_data(filename):
    with open(filename, 'r') as file:
        output = file.read()
    return tuple(re.split(r'\s+</instance>\s+', output))  # returns instances as a list


# convert tweet into a set of tokens (bag of words) made up of the important words of the tweet
# stop words are removed, tweets are converted to all-lowercase, certain features are replaced with relevant tags
def get_bag(tweet):
    # Stop words borrowed from NLTK
    stop = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out',
            'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into',
            'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the',
            'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were',
            'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to',
            'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have',
            'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can',
            'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself',
            'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by',
            'doing', 'it', 'how', 'further', 'was', 'here', 'than'}
    stop = set(stop)

    # normalize tweet
    tweet = tweet.lower()  # make tweet lowercase
    # tweet = re.sub(r'\@*', r'<tag>', tweet)  # replace tags with tag tag
    tweet = re.sub(r'https?://[\S]*', r'<url>', tweet)  # replace URLs with url tag
    tweet = tweet.replace("'", "")  # remove apostrophes
    # tweet = tweet.replace("/", " ")  # remove forward slash  # results more accurate when slashes are kept intact
    # Replace :), :-), :D, :-D, ;), ;-) with happy tag
    tweet = re.sub(r':-?\)', r'<happy>', tweet)
    tweet = re.sub(r':-?D', r'<happy>', tweet)
    tweet = re.sub(r';-?\)', r'<happy>', tweet)
    # Replace :(, :-(, >:(, >:-( with sad tag
    tweet = re.sub(r'>?:-?\(', r'<sad>', tweet)

    # create tokens from tweet, split at spaces, punctuation, and numbers
    tokens = set(re.split(r'[\s0-9().,;:!?"]+', tweet))
    tokens.discard("")

    # remove tokens without stop words
    return tokens - stop


# Cleaned instance (information between <instance> and </instance> tags) is passed through this method, which
# extracts instance ID, sentiment tag (for training data), and tweet (in the form of bag of words).
def extract_properties(instance):
    properties = re.search(
        (r'\s*<instance\s*id="([^"]+)">'  # Get instance ID
         r'(.*)'  # Get answer instance and sentiment in training data
         r'\s*<context>\s*'  # Capture context tag between above tag(s) and tweet
         r'(.*)'  # Get tweet
         r'\s*</context>\s*\Z'  # End of instance
         ), instance, re.VERBOSE | re.DOTALL)  # ignore white space and match all characters including newline

    # First 2 and final 2 tags of the training and test files don't fit the pattern, return None
    if properties is None:
        return None

    instance_id = properties.group(1)
    sentiment = properties.group(2)

    #  Only training data has labeled sentiment. Test data does not.
    if sentiment:
        label = re.search(r'sentiment="([^"]+)"/>', sentiment)
        if label:
            sentiment = label.group(1)
        else:
            sentiment = None

    tweet = properties.group(3)
    # get bag of words from tweet
    bag = get_bag(tweet)

    return instance_id, sentiment, bag


# Creates dictionary and frequency lists for all sentiments and word-sentiment pairs from training data
def create_train_dict(data):
    global wordsent_freq
    global sent_freq
    train_dict = dict()

    for instance in data:
        properties = extract_properties(instance)
        if not properties:  # First 2 and final 2 tags of the training and test files don't fit the pattern
            continue
        train_dict[properties[0]] = tuple(properties[1:])  # populate dictionary with ids and bag-of-words

    # increment respective frequency table for each occurrence of sentiment and word/sentiment pair
    for instance in train_dict:
        sentiment, bag = train_dict[instance]
        sent_freq[sentiment] += 1
        for word in bag:
            wordsent_freq[tuple((sentiment, word))] += 1

    # record frequency information to model log
    model = "Training Data Sentiment Frequency Table:\n"
    for sentiment in sent_freq:
        model += sentiment + ": " + str(sent_freq[sentiment]) + "\n"

    model += "\nTraining Data Word-Sentiment Pair Frequency Table:\n"
    for pair in wordsent_freq:
        model += str(pair) + ":\t" + str(wordsent_freq[pair]) + "\n"
    # print(str(wordsent_freq))
    # print(model)

    with open(model_filename, 'w') as m:
        m.write(model)

    return train_dict


# Takes frequency lists and test data to predict most likely tweet sentiment
# The formulas used to calculate the probability that a bag of words expresses a particular sentiment:
# The product of P(sentiment) and (P(word|sentiment) for all of the above collocations)
# For numerical stability, the log version is used:
# log(P(sentiment)) + summation of log(freq(word AND sentiment)/freq(sentiment)) for each word in bag.
def get_sentiment(bag):
    sent_log_prob = dict()

    for sent in sent_freq:
        # sentiment log prob: log(P(sentiment)) = log(sentiment frequency/ total number of training instances)
        log_probability = log(sent_freq[sent] / len(train_data))
        # summation of log probabilities of all sentiment/word combinations
        for word in bag:
            if wordsent_freq[sent, word]:
                log_probability += log(wordsent_freq[sent, word] / sent_freq[sent])
        sent_log_prob[sent] = log_probability

    # return prediction and associated log-probability
    return min(sent_log_prob, key=lambda k: sent_log_prob[k]), \
           sent_log_prob[min(sent_log_prob, key=lambda k: sent_log_prob[k])]


# Parses test data, passes instances to get_sentiment for sentiment prediction.
# Appends results to both output and log files on the fly.
# Returns output as string that can be used in the main method
def process_test_data(test_instances):
    output = ""
    with open(model_filename, 'a') as model:
        model.write("\nSentiment Analysis for Test Data:\n\nInstance ID\t\tPredicted Sentiment\tLog-Likelihood"
                    "\tBag-of-Words\n")
        for instance in test_instances:
            # extract properties from test data
            properties = extract_properties(instance)
            if not properties:  # first and final two lines of test data file don't fit pattern
                continue
            instance_id = properties[0]
            # test data does not have sentiment ID, so run bag of words through get_sentiment to get sense prediction
            predicted_sentiment, probability = get_sentiment(properties[2])
            model.write(instance_id + "\t\t" + predicted_sentiment + "\t" +
                        str(probability) + "\t" + str(properties[2]) + "\n")
            # append prediction to output in proper format
            output += '<answer instance="' + instance_id + '" sentiment="' + predicted_sentiment + '"/>\n'

    return output


def print_error():
    print('Invalid arguments. Please enter properly formatted arguments:')
    print('python sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt')
    print('\nReplace "sentiment-train.txt" with the name of the training file,')
    print('"sentiment-test.txt" with the name of the test file,')
    print('"my-model.txt" with the desired name of the log file outputted by this program,')
    print('and "my-sentiment-answers.txt" with your desired output file name.')
    print('Ensure trainer and test files are placed in the same directory as sentiment.py.')
    print('If no arguments are entered after sentiment-train.txt and sentiment-test.txt,')
    print('then the name of the log and output files will default respectively to')
    print('"my-model.txt.txt" and "my-sentiment-answers.txt."')
    return None


def main():
    global train_data
    global model_filename
    global output_filename
    # Print error and exit if training and test files are not specified in the command line
    if len(argv) < 3:
        print_error()
        exit()

    if len(argv) >= 4:
        model_filename = argv[3]
    else:
        model_filename = "my-model.txt"

    # if len(argv) >= 5 and argv[4] == ">":
    #     output_filename = argv[5]
    # else:
    #     output_filename = "my-sentiment-answers.txt"

    train_data = create_train_dict(import_data(argv[1]))
    test_instances = import_data(argv[2])
    # print(train_data)
    # print(len(train_data))
    # print(wordsent_freq)
    # print(test_instances)

    output = process_test_data(test_instances)

    # with open(output_filename, "w") as output_file:
    #     output_file.write(output)

    print(output)


if __name__ == "__main__":
    main()
