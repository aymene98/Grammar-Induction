import nltk
from nltk import parse
from nltk import CFG
import tagging
from nltk.parse import ShiftReduceParser

# readding grammar
def get_grammar_path(path):
    return nltk.data.load(path)

def get_grammar_string(string):
    return CFG.fromstring(string)

# splitting the text into sentences then tagging each sentence.
def split_text_to_sents(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = [sentence for sentence in sent_detector.tokenize(text)]
    tags_and_sents = []
    for sent in sentences:
        tags_and_sents.append((sent, tagging.pos_tags(sent)))
    return tags_and_sents

# using the grammar and the POS-tags that we got from the previous functions 
# we try to find at least a parsing tree.
def parse(grammar, text, RDP=True):
    parser = nltk.RecursiveDescentParser(grammar)
    if not RDP:
        parser = ShiftReduceParser(grammar)
    
    tags_and_sents = split_text_to_sents(text)
    sents_and_trees = [(sent[0], sent[1], parser.parse(sent[1])) for sent in tags_and_sents]
    return sents_and_trees # contains tuples (words, tags, trees)
