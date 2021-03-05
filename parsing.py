import nltk
from nltk import parse
from nltk import CFG
import tagging
from nltk.parse import ShiftReduceParser
from PyQt5.QtCore import QThread, pyqtSignal

# readding grammar


def get_grammar_path(path):
    return nltk.data.load(path)


def get_grammar_string(string):
    return CFG.fromstring(string)

# splitting the text into sentences then tagging each sentence.


def split_text_to_sents(text, tagger_type, new):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = [sentence for sentence in sent_detector.tokenize(text)]
    tags_and_sents = []
    for sent in sentences:
        tags_and_sents.append((sent, tagging.pos_tags(sent, tagger_type, new)))
    return tags_and_sents

# using the grammar and the POS-tags that we got from the previous functions
# we try to find at least a parsing tree.


def parse(grammar, text, tagger_type, new):
    #parser = nltk.RecursiveDescentParser(grammar)
    parser = ShiftReduceParser(grammar)
    tags_and_sents = split_text_to_sents(text, tagger_type, new)
    #sents_and_trees = [(sent[0], sent[1], parser.parse(sent[1])) for sent in tags_and_sents]
    sents_and_trees = []
    for sent in tags_and_sents:
        parsings = []
        for tree in parser.parse(sent[1]):
            parsings.append(tree)
        sents_and_trees.append((sent[0], sent[1], parsings))
    return sents_and_trees  # contains tuples (words, tags, trees)


class Parser(QThread):
    sents_and_trees = pyqtSignal(list)

    def __init__(self, parent=None, grammar='', text='', tagger_type="POS-tag du corpus", new=False):
        super().__init__(parent=parent)
        self.grammar = grammar
        self.text = text
        self.tagger_type = tagger_type
        self.new = new

    def run(self):
        parser = ShiftReduceParser(self.grammar)
        tags_and_sents = split_text_to_sents(
            self.text, self.tagger_type, self.new)
        sents_and_trees = []
        for sent in tags_and_sents:
            parsings = []
            for tree in parser.parse(sent[1]):
                parsings.append(tree)
            sents_and_trees.append((sent[0], sent[1], parsings))
        # contains tuples (words, tags, trees)
        self.sents_and_trees.emit(sents_and_trees)
