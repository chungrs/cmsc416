"""
Programming Assignment 3 - POS Tagging - Scorer

Roy Chung
20210314
CMSC 416-001

scorer.py is a program that accompanies tagger.py, a program that POS-tags a user-specified file with training data.
This program compares the output file generated by tagger.py against a key and calculates the accuracy of tagger.py.
In addition, it also generates a confusion matrix.

"""

from sys import argv
import pandas as pd
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


def create_array(pair_list):
    output_array = []
    for word_tag_pair in pair_list:
        current_pair = re.split('/', word_tag_pair)
        output_array.append(current_pair[1].split('|')[0])
    return output_array


# Calculate score
def scorer(prediction, key):
    match = 0
    total = len(key)  # Denominator is the number of tagged pairs

    # Iterate through key array, if there's a match with prediction array, then iterate match
    #
    for i in range(len(key)):
        if prediction[i] == key[i]:
            match += 1

    return match / total


def create_confusion_matrix(prediction, key):
    y_actual = pd.Series(key, name="Actual Tag")
    x_prediction = pd.Series(prediction, name="Predicted Tag")

    # These four settings make Panda display the whole matrix
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    return pd.crosstab(y_actual, x_prediction)


def write_to_file(score, matrix, filename):
    with open(filename, "w") as output_file:
        output_file.write("The accuracy of tagger.py is: " + str.format('{0:.2f}', score) + "%.\n\n" + matrix.to_string())

    return None


# Prints error message for improper command line arguments
def print_error():
    print('Invalid arguments. Please enter properly formatted arguments:')
    print('python scorer.py pos-test-with-tags.txt pos-test-key.txt > pos-tagging-report.txt')
    print('\nReplace "pos-test-with-tags.txt" with the name of the output file generated by tagger.py,')
    print('"pos-test-key.txt" with the name of the test key file,')
    print('and "pos-tagging-report.txt" with your desired output file name.')
    print('Ensure all files are placed in the same directory as scorer.py.')
    print('If no arguments are entered after pos-test-with-tags.txt and pos-test-key.txt,')
    print('then the name of the output file will default to "pos-tagging-report.txt."')
    return None


def main():
    # Print error and exit if training and test files are not specified in the command line
    if len(argv) < 3:
        print_error()
        exit()

    prediction_array = create_array(import_data(argv[1]))
    actual_array = create_array(import_data(argv[2]))
    # print(actual_array)

    score = scorer(prediction_array, actual_array) * 100
    confusion_matrix = create_confusion_matrix(prediction_array, actual_array)

    # print("The accuracy of tagger.py is: " + str.format('{0:.2f}', score) + "%.")
    # print(confusion_matrix)

    # Obtain output filename from command line, or give it default name
    if len(argv) >= 5 and argv[3] == ">":
        output_filename = argv[4]
    else:
        output_filename = "pos-tagging-report.txt"

    write_to_file(score, confusion_matrix, output_filename)

    print('Success! Open "' + output_filename + '" in the current directory to view report.')


if __name__ == "__main__":
    main()
