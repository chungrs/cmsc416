"""
Programming Assignment 4 - Word Sense Disambiguation

Roy Chung
20210330
CMSC 416-001

wsd.py is a program that takes as input a training file containing the word the user seeks to disambiguate used
in context that is tagged with the word sense. This is done based on the research of David Yarowsky, who
created a decision list algorithm designed to automatically restore the accent marks of Spanish and French words.
Since the restoration of accent marks was done based on context, the same logic could be applied for words
that are spelled the same, but with different meanings. Examples include the word bat, which can refer to a
specific type of flying rodent or a blunt instrument; or well, which can mean "good" or refer to a source of water.
Though this program is designed to work with any word given properly formatted training and test data, it was
tested on the word "line," which in the training and test data meant either a product line or a telephone line.
The program outputs the tagged test file as a plain text file whose filename is determined by command line arguments.

Collocations considered when predicting the word sense are as follows:
-1 W - the word immediately to the left of the ambiguous word
+1 W - the word immediately to the right of the ambiguous word
Word found in +/-K word window (this program uses 4 as the value for K, as recommended in Yarowsky's paper)
-2W, -1W - pair of words immediately to the left of the ambiguous word
-1W, +1W - pair of words, one immediately to the left and the other immediately to the right of the ambiguous word
+1W, +2W - pair of words immediately to the right of the ambiguous word

The following are the formulas used to calculate the probability that a given instance of a word has a
particular word sense:
The product of P(Sense) and (P(collocation|sense) for all of the above collocations)

For numerical stability, the log version is used:
log(P(sense)) + summation of log(freq(collocation AND sense)/freq(sense)) for each of the above collocations.

Here is an example of how training data should be formatted:
<corpus lang="en">
<lexelt item="line-n">
<instance id="line-n.w9_10:6830:">
<answer instance="line-n.w9_10:6830:" senseid="phone"/>
<context>
 <s> The New York plan froze basic rates, offered no protection to Nynex against an economic downturn that sharply cut
 demand and didn't offer flexible pricing. </s> <@> <s> In contrast, the California economy is booming, with 4.5% access
 <head>line</head> growth in the past year. </s>
</context>
</instance>
<instance id="line-n.w8_057:16550:">
<answer instance="line-n.w8_057:16550:" senseid="product"/>
<context>
 <s> According to analysts, sales of PS/2 got off to a rocky start but have risen lately -- especially in Europe. </s>
 <@> <s> IBM wants to establish the <head>line</head> as the new standard in personal computing in Europe. </s> <@> <s>
  It introduced the line in April 1987 and has said it shipped nearly two million units by its first anniversary. </s>
</context>
</instance>
<instance id="line-n.w9_32:5971:">
<answer instance="line-n.w9_32:5971:" senseid="product"/>
<context>
 <s> Culinova fresh entrees, launched in 1986 by Philip Morris Cos.'s General Foods Corp., hit similar distribution
 problems. </s> <@> <s> Last December, shortly after Philip Morris bought Kraft Inc., the struggling <head>line</head>
 was scrapped. </s>
</context>
</instance>
</lexelt>
</corpus>

Test data is formatted similarly, but without "senseid" in the instance tag.

For a more detailed explanation of this algorithm, please refer to "Decision Lists for Lexical Ambiguity Resolution:
Application to Accent Restoration in Spanish and French" by David Yarowsky, published in 1994.

Results can be scored by comparing the output file to the key using the accompanying scorer.py.

The accuracy of my text run was: 73.81%, with the following confusion matrix:

Predicted Word Sense  phone  product
Actual Word Sense
phone                    56       16
product                  17       37

The most frequent sense baseline for this particular dataset was 52.41%
The most frequent word sense was "product" with a total number of 196 occurrences out of 374 instances.

To run this program, place the training and test files into the same directory as wsd.py,
and enter the following into the command line:

python wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt

Replace "line-train.txt" with the name of the training file, "line-test.txt" with the name of the test file,
"my-model.txt" with the desired name of the log file outputted by this program, and "my-line-answers.txt" with your
desired output file name. Ensure trainer and test files are placed in the same directory as wsd.py.
If no arguments are entered after line-train.txt and line-test.txt, then the name of the log and output files will
default respectively to "my-model.txt.txt" and "my-line-answers.txt."
"""

from sys import argv
import re
from math import log
from collections import Counter

# ##########Global Variables##########
# Frequency lists
freq_sense, freq_l1w, freq_r1w, freq_l2w, freq_l1r1, freq_r2w, freq_win = \
        Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
training_data = ()  # Training Data
training_dict = dict()  # Training Dictionary
model_filename = ""
# ##########Global Variables##########


def import_data(filename):
    with open(filename, 'r') as file:
        output = file.read()
    return tuple(re.split(r'\s+</instance>\s+', output))  # returns instances as a list


# Cleaned instance (information between <instance> and </instance> tags) is passed through this method, which
# extracts instance ID, sense ID, and collocations.
def extract_properties(instance):
    properties = re.search(
        (r'\s*<instance\s*id="([^"]+)">'  # Get instance ID
         r'(.*)'  # Get sense ID between instance and context tags
         r'\s*<context>\s*'  # Capture context tag between sense and s tags
         r'.*<s>(.*)\s*<head>.*'  # Get sentence segment between <s> and <head> tags.
         r'</head>\s*([^<]*)<'  # Get sentence segment between </head> and </s> tags.
         ), instance, re.VERBOSE | re.DOTALL)  # ignore white space and match all characters including newline

    # First 2 and final 2 tags of the training and test files don't fit the pattern, return None
    if properties is None:
        return None

    instance_id = properties.group(1)

    # Only training data has sense_id - test data does not
    sense_id = properties.group(2)
    is_sense = re.search(r'senseid="([^"]+)"/>', sense_id)
    if is_sense:
        sense_id = is_sense.group(1)
    else:
        sense_id = None

    # List of words from the sentence segment leading up to the ambiguous word (not inclusive)
    # Punctuations and other non-alphabetic characters are removed
    pt1 = [word for word in re.split(r'[\s.,!?0-9]+', properties.group(3)) if word]

    # Punctuations and other non-alphabetic characters are removed
    # List of words from the sentence segment following the ambiguous word (not inclusive)
    pt2 = [word for word in re.split(r'[\s.,!?0-9]+', properties.group(4)) if word]

    # get collocations
    # -1 W - word immediately to the left of ambiguous word
    l1w = pt1[-1] if pt1 else None  # address the possibility that ambiguous word might be first word in sentence
    # +1 W - word immediately to the right of ambiguous word
    r1w = pt2[0] if pt2 else None  # address the possibility that ambiguous word might be last word in sentence
    # -2 W - pair of words immediately to the left of ambiguous word
    l2w = tuple((pt1[-2], l1w)) if len(pt1) >= 2 else None
    # -1 W and +1 W - pair of words immediately to the left and right of ambiguous word
    l1r1 = tuple((l1w, r1w)) if l1w and r1w else None
    # +2 W - pair of words immediately to the right of ambiguous word
    r2w = tuple((r1w, pt2[1])) if len(pt2) >= 2 else None

    # Get words found in +/-K word window (+-k W), here we will use 4 for K as suggested by Yarowsky in the foothotes
    # of his research paper
    win = pt1[-4:] if len(pt1) >= 4 else pt1[:]
    win += pt2[:4] if len(pt2) >= 4 else pt2[:]
    # Store as set, since only occurrence matters. Order and frequency don't matter.
    win = set(win)

    return instance_id, sense_id, l1w, r1w, l2w, l1r1, r2w, win


# Create dictionary from training data
def create_training_dict(data):
    train_dict = dict()
    for instance in data:
        properties = extract_properties(instance)
        if not properties:  # First 2 and final 2 tags of the training and test files don't fit the pattern
            continue
        train_dict[properties[0]] = tuple(properties[1:])  # populate dictionary with ids and collocations
    return train_dict


# Creates frequency lists for all senses and collocations
def generate_freq_lists():
    # Create counters for all collocations and senses
    global freq_sense
    global freq_l1w
    global freq_r1w
    global freq_l2w
    global freq_l1r1
    global freq_r2w
    global freq_win

    # Iterate through training_dict and get frequencies for all sense/collocation combinations
    for instance in training_dict:
        sense, l1w, r1w, l2w, l1r1, r2w, win = training_dict[instance]
        freq_sense[sense] += 1
        # use if statements because not all instances have complete collocations
        if l1w:
            freq_l1w[tuple((sense, l1w))] += 1
        if r1w:
            freq_r1w[tuple((sense, r1w))] += 1
        if l2w:
            freq_l2w[tuple((sense, l2w))] += 1
        if l1r1:
            freq_l1r1[tuple((sense, l1r1))] += 1
        if r2w:
            freq_r2w[tuple((sense, r2w))] += 1
        if win:
            for word in win:
                freq_win[tuple((sense, word))] += 1

    # print(freq_sense)
    # print(freq_l1w)
    # print(freq_r1w)
    # print(freq_l2w)
    # print(freq_l1r1)
    # print(freq_r2w)
    # print(freq_win)

    # Write frequency stats to model log
    model_output = "Training data information:\n\nWord sense frequency:\n"
    for each in freq_sense:
        model_output += (each + ": " + str(freq_sense[each]) + "\n")

    model_output += "\n-1W frequency:\n"
    for each in freq_l1w:
        model_output += str(each) + "\t\t" + str(freq_l1w[each]) + "\n"

    model_output += "\n+1W frequency:\n"
    for each in freq_r1w:
        model_output += str(each) + "\t\t" + str(freq_r1w[each]) + "\n"

    model_output += "\n-2W, -1W frequency:\n"
    for each in freq_l2w:
        model_output += str(each) + "\t\t" + str(freq_l2w[each]) + "\n"

    model_output += "\n-1W, +1W frequency:\n"
    for each in freq_l1r1:
        model_output += str(each) + "\t\t" + str(freq_l1r1[each]) + "\n"

    model_output += "\n+1W, +2W frequency:\n"
    for each in freq_r2w:
        model_output += str(each) + "\t\t" + str(freq_r2w[each]) + "\n"

    with open(model_filename, 'w') as model:
        model.write(model_output)

    return freq_sense, freq_l1w, freq_r1w, freq_l2w, freq_l1r1, freq_r2w, freq_win


# Takes frequency lists, number of training instances, and test data to predict word sense
# Appends results to both output and log files on the fly.
# Returns output as string that can be used in the main method
def process(test_data):
    output = ""
    # Write results into log as they're calculated
    with open(model_filename, 'a') as model:
        model.write("\nWSD Results for Test Data:\n\nInstance ID\t\tPredicted Word Sense\n")
        for instance in test_data:
            # extract collocations from test data
            properties = extract_properties(instance)
            if not properties:
                continue
            instance_id = properties[0]
            # test data does not have sense ID, so run collocations into wsd function to get sense prediction
            predicted_sense = wsd(properties[2:])

            model.write(instance_id + "\t\t" + predicted_sense + "\n")
            # append prediction to output in proper format
            output += '<answer instance="' + instance_id + '" senseid="' + predicted_sense + '"/>\n'

    return output


# returns the most likely word sense for a word given its collocations
def wsd(collocations):
    # do not include window frequency list from lists to be iterated since it needs to be processed differently
    freq_lists = freq_l1w, freq_r1w, freq_l2w, freq_l1r1, freq_r2w
    l1w, r1w, l2w, l1r1, r2w, win = collocations
    # remove win from collocations list since they need to be handled differently
    collocations = l1w, r1w, l2w, l1r1, r2w

    sense_log_probabilities = dict()
    for sense in freq_sense:
        # log(P(sense)) = log(sense frequency/ total number of training instances)
        log_probability = log(freq_sense[sense] / len(training_dict))
        # summation of log probabilities of all sense/collocation combinations
        for coll, freq_list in zip(collocations, freq_lists):
            if freq_list[sense, coll] > 0:
                log_probability += log(freq_list[sense, coll] / freq_sense[sense])
        # log probability that a word is within +/- words of the ambiguous word
        for each in win:
            if freq_win[sense, each]:
                log_probability += log(freq_win[sense, each] / freq_sense[sense])
        sense_log_probabilities[sense] = log_probability

    return min(sense_log_probabilities, key=lambda k: sense_log_probabilities[k])


# Prints error message for improper command line arguments
def print_error():
    print('Invalid arguments. Please enter properly formatted arguments:')
    print('python wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt')
    print('\nReplace "line-train.txt" with the name of the training file,')
    print('"line-test.txt" with the name of the test file,')
    print('"my-model.txt" with the desired name of the log file outputted by this program,')
    print('and "my-line-answers.txt" with your desired output file name.')
    print('Ensure trainer and test files are placed in the same directory as wsd.py.')
    print('If no arguments are entered after line-train.txt and line-test.txt,')
    print('then the name of the log and output files will default respectively to')
    print('"my-model.txt.txt" and "my-line-answers.txt."')
    return None


def main():
    global training_data
    global training_dict
    global model_filename
    # Print error and exit if training and test files are not specified in the command line
    if len(argv) < 3:
        print_error()
        exit()

    if len(argv) >= 4:
        model_filename = argv[3]
    else:
        model_filename = "my-model.txt"

    # if len(argv) >= 6 and argv[4] == ">":
    #     output_filename = argv[5]
    # elif len(argv) >= 5 and argv[4] != ">":
    #     output_filename = argv[4]
    # else:
    #     output_filename = "my-line-answers.txt"

    training_data = import_data(argv[1])
    training_dict = create_training_dict(training_data)

    test_data = import_data(argv[2])

    generate_freq_lists()

    output = process(test_data)
    print(output)

    # with open(output_filename, "w") as output_file:
    #     output_file.write(output)


if __name__ == "__main__":
    main()
