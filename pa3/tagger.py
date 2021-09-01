"""
Programming Assignment 3 - POS Tagging - Tagger

Roy Chung
20210314
CMSC 416-001

tagger.py is a program that takes as input a training file containing part of speech tagged text, and  a file
containing text to be part of speech tagged. This program uses the training data to determine the most likely
tag for each word in the text to be tagged.

Each word in the training data is assigned a POS tag that maximizes P(tag|word). This is done by looking at the most
likely tag for each word in the training data, as well as the mostly likely tag that follows the previous tag.
Words in the test data not found in the training data is assumed to be a singular/mass noun and given an "NN" tag.

The following are the formulas used to calculate the probability that a given word has a particular tag:
P(tag|word) = P(word|tag) * P(tag|tag-1)
P(word_i|tag_i) = freq(tag_i, word_i)/freq(tag_i)
P(tag_i|tag_i-1) = freq(tag_i-1|tag_i)/freq(tag_i)

The program outputs the tagged test file as a plain text file whose filename is determined by command line arguments.

Results can be scored by comparing the output file to the key using the accompanying scorer.py.

To run this program, place the training and test files into the same directory as pagger.py,
and enter the following into the command line:

python tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt
Replace "pos-train.txt" with the name of the training file, "pos-test.txt" with the name of the test file,
and "pos-test-with-tags.txt" with your desired output file name. If no arguments are entered after pos-train.txt and
pos-test.txt, then the name of the output file will default to "pos-test-with-tags.txt."
"""

from sys import argv
import re


# Reads text files and returns them as a string list with brackets removed
def import_data(filename):
    output = ""
    with open(filename, 'r') as data:
        output += data.read()
    output = re.sub(r"[\[\]]", "", output)
    # Replace forward slashes in text file that aren't delineators with <FWD_SLASH> tag.
    # This will be undone after words and tags are separated in create_freq_tables
    output = output.replace("\/", "<FWD_SLASH>")
    return output.split()


# Create Word/Tag and Tag/Tag-1 frequency tables from training list created from training file
def create_freq_tables(training_list):
    word_tag_freq = {}
    tag_tag1_freq = {}
    tag_freq = {}
    tag1 = None

    # iterate through all word/tag pairs in training list
    for word_tag_pair in training_list:
        # split current pair into word and tag
        current_pair = re.split('/', word_tag_pair)
        word = current_pair[0].replace("<FWD_SLASH>", "\/")  # replace <FWD_SLASH> tag generated in import_data with \/
        tag = current_pair[1].split('|')[0]  # If a tag has a | symbol (e.g. NN|JJ), only use first part

        if tag not in tag_freq:
            tag_freq[tag] = 1
        else:
            tag_freq[tag] += 1

        # populate word + tag frequency table with frequency of each word+tag combination
        if word in word_tag_freq:
            if tag in word_tag_freq[word]:
                word_tag_freq[word][tag] += 1
            else:
                word_tag_freq[word][tag] = 1
        else:
            word_tag_freq[word] = {}
            word_tag_freq[word][tag] = 1

        # populate tag + tag-1 frequency table with frequency of each word+tag combination
        if tag1 in tag_tag1_freq:
            if tag in tag_tag1_freq[tag1]:  # if tag-1|tag is in array, iterate
                tag_tag1_freq[tag1][tag] += 1
            else:
                tag_tag1_freq[tag1][tag] = 1  # if tag1 is in array but tag is not, make tag-1|tag equal to 1
        elif tag1 is not None:  # if neither is in array, create element for tag-1|tag and make it equal to 1
            tag_tag1_freq[tag1] = {}
            tag_tag1_freq[tag1][tag] = 1
        #  If tag1 is None, skip this step for current loop

        # set tag-1 equal to current tag before repeating loop
        tag1 = tag

    return word_tag_freq, tag_tag1_freq, tag_freq


# POS-tags test data
def pos_tagger(test_data, word_tag_freq, tag_tag1_freq, tag_freq_table):
    tagged_words = []
    tag1 = None

    for word in test_data:
        max_prob = 0  # used to store maximum P(tag|word)

        # replace <FWD_SLASH> tag generated in import_data with \/
        word = word.replace("<FWD_SLASH>", "\/")

        # assume any word found in test data that's not in training data is a singular/mass noun (NN)
        if word not in word_tag_freq:
            tagged_words.append(word + '/' + 'NN')
            tag1 = 'NN'
            continue

        # First word case (no tag-1)
        if tag1 is None:
            # find tag that maximizes P(word|tag)
            for tag, tag_freq in word_tag_freq[word].items():
                # P(word|tag) = freq(tag, word) / freq(tag)
                current_prob = word_tag_freq[word][tag] / tag_freq_table[tag]
                if current_prob > max_prob:  # if current_prob > stored max_prob, update max_prob and max_tag
                    max_prob = current_prob
                    max_tag = tag

            # --------- Begin custom rules: ---------
            # If a word is uppercase and the the tag of the previous word is not a sentence-final punctuation,
            # assume proper noun
            if word.isupper():
                if tag1 != ".":
                    max_tag == "NNP"
                    tag == "NNP"
                    if word.endswith('s'):
                        max_tag == "NNPS"
                        tag == "NNPS"

            if word == "''":
                max_tag = "''"
                tag = "''"

            if word == "#":
                max_tag = "#"
                tag = "#"

            if word == "$":
                max_tag = "$"
                tag = "$"

            if word == ",":
                max_tag = ","
                tag = ","

            if word == ":":
                max_tag = ":"
                tag = ":"

            # if word is a !, ., or ?, it is a sentence-final punctuation (".")
            if re.match(r"^[!.?]+$", word):
                max_tag = "."
                tag = "."

            # if a word begins with a number and ends with an 's,' assume plural proper noun (e.g. Boeing *757s*)
            if word[0].isnumeric():
                if word.endswith('s'):
                    max_tag = "NNPS"
                    tag = "NNPS"
            # ---------- End custom rules: ----------

            tagged_words.append(word + '/' + max_tag)
            tag1 = tag
            continue

        # All other cases
        for tag, tag_freq in word_tag_freq[word].items():
            if tag not in tag_tag1_freq[tag1]:
                continue

            # P(tag|word) * P(tag|tag-1) = (freq(tag, word) / freq(tag)) * (freq(tag-1, tag) / freq(tag-1))
            current_prob = (word_tag_freq[word][tag] / tag_freq_table[tag]) * \
                           (tag_tag1_freq[tag1][tag] / tag_freq_table[tag1])

            # if current_prob > stored max_prob, update max_prob and max_tag
            if current_prob > max_prob:
                max_prob = current_prob
                max_tag = tag

        # --------- Begin custom rules: ---------
        # If a word is uppercase and the the tag of the previous word is not a sentence-final punctuation,
        # assume proper noun
        if word.isupper():
            if tag1 != ".":
                max_tag == "NNP"
                tag == "NNP"
                if word.endswith('s'):
                    max_tag == "NNPS"
                    tag == "NNPS"

        if word == "''":
            max_tag = "''"
            tag = "''"

        if word == "#":
            max_tag = "#"
            tag = "#"

        if word == "$":
            max_tag = "$"
            tag = "$"

        if word == ",":
            max_tag = ","
            tag = ","

        if word == ":":
            max_tag = ":"
            tag = ":"

        if re.match(r"^[!.?]+$", word):
            max_tag = "."
            tag = "."

        #if a word begins with a number and ends with an 's,' assume plural proper noun (e.g. Boeing *757s*)
        if word[0].isnumeric():
            if word.endswith('s'):
                max_tag = "NNPS"
                tag = "NNPS"
        # ---------- End custom rules: ----------

        tagged_words.append(word + '/' + max_tag)
        tag1 = tag

    return tagged_words


# Writes list to plain text file
def write_to_file(tagged_words, filename):
    with open(filename, "w") as output_file:
        output_file.write("\n".join(tagged_words))
    return None


# Prints error message for improper command line arguments
def print_error():
    print('Invalid arguments. Please enter properly formatted arguments:')
    print('python tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt')
    print('\nReplace "pos-train.txt" with the name of the training file,')
    print('"pos-test.txt" with the name of the test file,')
    print('and "pos-test-with-tags.txt" with your desired output file name.')
    print('Ensure trainer and test files are placed in the same directory as tagger.py.')
    print('If no arguments are entered after pos-train.txt and pos-test.txt,')
    print('then the name of the output file will default to "pos-test-with-tags.txt."')
    return None


def main():
    # Print error and exit if training and test files are not specified in the command line
    if len(argv) < 3:
        print_error()
        exit()

    # Process training data and store in list
    training_data = import_data(argv[1])
    # print(training_data)

    # Process test data and store in list
    test_data = import_data(argv[2])
    # print(test_data)

    # Obtain Word/Tag and Tag/Tag-1 frequency tables from training data
    word_tag_freq, tag_tag1_freq, tag_freq = create_freq_tables(training_data)
    # print(word_tag_freq)
    # print(tag_tag1_freq)
    # print(tag_freq)

    # Obtain POS-tagged word list
    tagged_words = pos_tagger(test_data, word_tag_freq, tag_tag1_freq, tag_freq)
    # print(tagged_words)

    # Obtain output filename from command line, or give it default name
    if len(argv) >= 5 and argv[3] == ">":
        output_filename = argv[4]
    else:
        output_filename = "pos-test-with-tags.txt"

    # Write the POS-tagged list to a plain text file
    write_to_file(tagged_words, output_filename)

    print('Success! Open "' + output_filename + '" in the current directory to view the POS-tagged test data.')


if __name__ == "__main__":
    main()
