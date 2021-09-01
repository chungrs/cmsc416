# Programming Assignment 1 - Eliza
##########################################################
# Roy Chung
# 20210216
# CMSC 416-001
##########################################################
# Eliza is a chatbot intended to simulate a conversation
# with a therapist. It searches for defined language
# patterns in the user's input, and attempts to give a
# plausible response.
#
# Example input and output:
# <User> I want to rule the world.
# [Eliza] User, why do you want to rule the world?
# <User> I don't know, I think I crave power.
# [Eliza] Why don't you tell me more about your cravings.
##########################################################

import random
import re

# variables used by the program
user_input = ""  # stores user input to be processed
loop_on = True  # loop stays on until the user quits

print('''Chat with Eliza in plain English using proper spelling.
Enter "quit" when you are done with the session.''')
print("--------------------------------------------------------")

# Prompt user for name
print("[Eliza] Hi, I'm a psychotherapist. What is your name?")
user_name = input("<User> ")
user_name = re.sub("my name is ", "", user_name, flags=re.IGNORECASE)
user_name = re.sub(r"\.", "", user_name).title()

# Initialize dictionary of words/phrases to be reflected
# When restating user inputs, 1st and 2nd person terms and helpers must be reflected
reflections = {
    "i": "you",
    "me": "you",
    "you": "me",
    "my": "your",
    "your": "my",
    "mine": "yours",
    "yours": "mine",
    "am": "are",
    "are": "am",
    "was": "were",
    "were": "was",
    "i'd": "you would",
    "i'll": "you will",
    "i've": "you have",
    "i'm": "you are",
    "you'd": "I would",
    "you'll": "I will",
    "you've": "I have",
    "you're": "I am"
}

# More specific patterns are placed towards the top so they aren't captured by the more general ones
# "%n" in responses means part of the user's statement will be restated
# There is at least one response for each pattern that will be chosen at random. The final "(.*)" captures all other
# statements not accounted for by the programmer.
responses = [(re.compile(pattern[0]), pattern[1]) for pattern in [
    # spots for various forms of the word "crave" and asks the user about cravings
    ["crav[e(ings?)]",
        ["Why don't you tell me more about your cravings?",
         user_name + ", could you tell me more about your cravings?"]],
    # spots for various forms of the word "desire" and asks about the user's desires
    ["(desires?|aspir(es?|ations?|ing))",
         ["Why don't you tell me more about what you want?",
         user_name + ", what are some of your goals in life??"]],
    # If depression is mentioned, Eliza will ask related questions
    ["[Dd]epress(ed|ion)",
        ["I am sorry to hear you are depressed.",
         "Do you know what is causing your depression?",
         "Why do you feel depressed?"]],
    # If depression is mentioned, Eliza will ask related questions
    ["[Aa]nxi(ous|ety)",
        ["Let's talk about what makes you anxious.",
         "Do you know what triggers your anxiety?",
         "Why do you feel anxious?"]],
    # If the user mentions something about ending the session, give instructions
    ["[Ee]nd ?(.*)? session",
        ['If you want to end this session, simply type the word "quit."',
         'Feel free to end our conversation at any time by typing the word "quit."']],
    # If the user says something about Eliza being a computer or a bot, give a plausible response
    ["[Yy]ou(\'?re)? (.*) (computer|bot)",
        ["Yes, I am a computer, but I will still do my best to help you.",
         "I may not be a real person, but I can still listen to what's on your mind.",
         "I guess the cat's out the bag."]],
    ["[Ii] think (.*)",
        ["Do you know why you think %1?",
         "Tell me more about why you think %1."]],
    ["[Ii] feel (.*)",
        ["Do you know why you feel %1?",
         "Tell me more about why you feel %1."]],
    ["[Ii] believe (.*)",
        ["Do you know why you believe %1",
         "Tell me more about why you believe %1",
         "You believe %1. Why is that?"]],
    # If the user answers a question in the affirmative, Eliza will ask the user to keep speaking
    [r"\b[Yy](es|eah|ea)\b",
        ["Please continue.",
         "Go on.",
         "And why is that?",
         "Tell me more."]],
    # If the user responds in the negative, Eliza responds by saying she understands.
    ["^[Nn]o(pe)?\.?$",
        ["I see.",
         "I understand."]],
    # If Eliza asks a question, there's a chance that the user will respond with a "because" statement.
    ["^[Bb]ecause",
        ["Do you think that explains how you feel?",
         "Let's talk more about this.",
         "I understand."]],
    ["[Ww]hy (are|don'?t) you",
        ["Let's ask less questions about me and talk more about you.",
         "Let's focus on you instead."]],
    # Why statements can be expected. Eliza tells the user to give more details.
    ["^[Ww]hy (.*)",
        ["What are your thoughts on why %1?",
         "Perhaps you can answer your own question if you talk about it some more."]],
    # capture "how are you" so it doesn't get mistaken for a more generic "how" question
    ["[Hh]ow are you\\??$",
        ["I'm doing well. And you?",
         "Fine, thank you.",
         "Great. How about you?"]],
    # answer "how" statements by restating.
    [r"\b^[Hh]ow\b (.*)",
        ["Perhaps you can answer your own question if you talk about it some more.",
         "I don't know how %1, but maybe we can figure something out if you talk more about how you feel."]],
    ["[Ww]ho are you\\??$",
        ["I am Eliza, your therapist."]],
    ["[Ww]hat('?s| is) your name\\??",
        ["My name is Eliza.",
         "My name is Eliza, and your name is " + user_name + ".",
         "I'm Eliza.",
         "Eliza.",
         "I'm Eliza, and you're " + user_name + "."]],
    # Offer condolences if the patient mentions death
    ["([Pp]assed away)|([Dd]ied)",
        ["I'm sorry for your loss. Would you like to tell me more?",
         "My condolences. Would talking about it make you feel better?"]],
    # Response if user says something like "sorry to bother you"
    [r"\b[Ss]orry\b",
        ["No need to apologize. I'm here to listen.",
         "Don't be sorry. I'm here to help."]],
    ["[Ii] feel (.*)",
        ["Why do you feel %1?",
         "Do you know why you feel %1?",
         "Tell me more about your feelings."]],
    ["[Ii] am (.*)",
        ["How does it feel to be %1?",
         "Why are you %1?",
         "Tell me more about why you are %1.",
         "Do you know the reason why you are %1?"]],
    ["[Ii]'m (.*)",
        ["How does it feel to be %1?",
         "Why are you %1?",
         "Tell me more about why you are %1.",
         "Do you know the reason why you are %1?"]],
    ["[Hh]elp me",
        ["I'm here to help.",
         "I'll do my best to help you work through your problems."]],
    # words like family, parents, mother, father are captured with the assumption that the user is speaking of family
    ["([Ff]amil(y|ial|ies)|[Pp]arent(al|s)?)",
        ["Tell me more about your family.",
         user_name + ", could you describe your relationship with you family?"]],
    [r"\b([Ff]ather)|([Dd]ad(dy)?)\b",
        ["Could you tell me more about your relationship with your father?",
         "Describe the relationship you have with your father."]],
    ["[Bb]rother",
        ["Could you tell me more about your relationship with your brother?",
         "Describe the relationship you have with your brother."
         "Talk to me about your brother."]],
    ["[Ss]ister",
        ["Could you tell me more about your relationship with your sister?",
         "Describe the relationship you have with your sister."
         "Tell me more about your sister."]],
    ["[Ss]ibling",
        ["Could you tell me more about your relationship with your siblings?",
         "Tell me more about your family."
         "Describe the relationship you have with your siblings."
         "Tell me more about your siblings."
         "Talk to me more about your siblings."]],
    [r"\b([Mm]other)|([Mm]om(my)?)\b",
        ["Could you tell me more about your relationship with your mother?",
         "Describe your relationship with your mother."]],
    # Responses to statements potentially about self-harm
    ["end (my life)|myself|(it all)",
        ["Have you ever thought about suicide before, or tried to harm yourself before?"]],
    ["(hurt|kill|cut|harm) myself",
        ["Have you ever thought about suicide before, or tried to harm yourself before?"]],
    # Experimenting with incomplete sentence.
    # "I'm going to burn your" might be responded to with "You're going to burn my what?"
    ["(.*) my$",
        ["%1 your what?",
         "Please speak in complete sentences."]],
    ["(.*) your$",
        ["%1 my what?",
         "Please speak in complete sentences."]],
    # Respond accordingly if user thanks Eliza
    ["[Tt]hank you",
        ["You're welcome.",
         "My pleasure."]],
    # Address user's wishes
    ["[Ii] want (.*)",
        ["Why do you want %1?",
         "I see. Could you elaborate more on why you want %1?",
         user_name + ", could you tell me more about why you want %1?"]],
    ["[Ii] need (.*)",
        ["Why do you think you need %1?",
         user_name + ", could you tell me what makes you believe you need %1?"]],
    # Divert "you" statements
    ["^[Yy]ou (.*)",
        ["What makes you think I %1?",
         "Why do you think I %1?",
         "Let's keep our conversation focused on you."]],
    # Chances are statements ending in you
    ["you\.?$",
        ["Let's keep this conversation about you.",
         "We're talking about you, not me.",]],
    # Divert the conversation if the user makes a statement about Eliza
    ["([Yy]ou'?re|[Yy]ou are)",
        ["Let's keep this conversation about you.",
         "We're talking about you, not me.",
         "Do you feel that way about other people as well?"]],
    # Say bye to the user if quit is entered
    ["^[Qq]uit\.?$",
        ["Thank you for visiting today. Hope you enjoy the rest of your day.",
         "It was a pleasure talking to you. Enjoy the rest of your day!",
         "Thank you for coming today. Goodbye."]],
    # Answer generic questions
    ["(.*)\?$",
        ["What do your gut instincts tell you?",
         "Perhaps if we talk some more, we can find some potential answers to your question."]],
    # Captures statements that don't fit the above patterns
    ["(.*)",
        ["I see.",
         "What do you mean when you say %1?",
         "What do you mean by that?",
         "I don't quite understand. Could you please give further details one at a time?",
         "%1?"]]
    ]
]


# Search user's input for keys found in the reflections list and replaces them with corresponding reflections
def reflect(fragment):
    # break fragment string into tokens
    tokens = re.findall(r"[\w']+", fragment.lower())
    # array for output
    output_tokens = []

    # iterate through tokens and replace words if they are in reflections as needed
    for i in tokens:
        output_tokens.append(reflections.get(i, i))

    # return output_tokens as string
    return ' '.join(output_tokens)


# Take user's input, run it through the list of regular expressions,
# and respond accordingly if a match is found.
def process(statement):
    for pattern, response in responses:  # Iterate through patterns in responses and find a match
        match = pattern.search(statement)
        if match is not None:
            # If the user's input matches a defined pattern, return one of the responses
            output = random.choice(response)
            while "%" in output:  # If a %n is found in the response, it is replaced.
                # find start index of where the statement should be replaced
                start_index = output.find("%")  # store index
                # Replace %n in canned response with a restatement of the user's input after reflecting the grammar
                output = output.replace(output[start_index:start_index + 2], reflect(match.group(1))).capitalize()
                output = re.sub(r"\bi\b", "I", output)  # if the output contains standalone lowercase "i," capitalize
                output = output.replace("me am ", "I am ")  # replace instances of "me am" with "I am"
            return output


# Begin conversation
print("[Eliza] Hello " + user_name + ". How can I help you today?")

# Conversation continues until the user enters "quit."
while loop_on:
    user_input = input("<" + user_name + "> ")
    if user_input == "quit." or user_input == "quit" or user_input == "Quit" or user_input == "Quit.":
        loop_on = False
    print("[Eliza] " + process(user_input))
