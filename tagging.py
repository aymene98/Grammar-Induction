import nltk
import re
import pickle
from PyQt5.QtCore import QThread
from reading_collection import get_corpus, get_sentences_word_pos
from corpus_utils import retrieve_corpus_sen_pos_tags


def tagger(taged_sents):
    t0 = nltk.DefaultTagger('NN')
    t1 = nltk.UnigramTagger(taged_sents, backoff=t0)
    t2 = nltk.BigramTagger(taged_sents, backoff=t1)
    t3 = nltk.NgramTagger(3, taged_sents, backoff=t2)
    t4 = nltk.NgramTagger(4, taged_sents, backoff=t3)
    return t4


# def create_tagger(name, simplify_tags=False, universal=False, path='../brown/brown/'):
#     word_pos_sentences = retrieve_corpus_sen_pos_tags(
#         path, remove_tokens=False, universal=universal, simplify_tags=simplify_tags)
#     t = tagger(word_pos_sentences)
#     pickle.dump(t, open("./taggers/"+name, "wb"))


def tag(sent, tagger_type, new=False):
    name = ""
    if tagger_type == "POS-tag du corpus":
        name = "./taggers/tagger_all"
    if tagger_type == "POS-tag modifiés":
        name = "./taggers/tagger_simplified"
    if tagger_type == "POS-tag universels":
        name = "./taggers/tagger_universal"
    if new:
        name += "_new"
    name += '.p'
    with open(name, "rb") as f:
        tagger = pickle.load(f)
        l = re.findall(r"[\w']+|[.,!?;]", sent)
        return tagger.tag(l)


def pos_tags(sent, tagger_type, new):
    return [t[1] for t in tag(sent, tagger_type, new)]


class TaggerCreator(QThread):
    def __init__(self, parent=None, corpus_path='brown/', filename='tagger.p', simplify_tags=False, universal=False) -> None:
        super().__init__(parent)
        self.corpus_path = corpus_path
        self.filename = filename
        self.simplify_tags = simplify_tags
        self.universal = universal

    def run(self):
        word_pos_sentences = retrieve_corpus_sen_pos_tags(
            self.corpus_path, remove_tokens=False, universal=self.universal, simplify_tags=self.simplify_tags)
        t = tagger(word_pos_sentences)
        with open("./taggers/"+self.filename, "wb") as f:
            pickle.dump(t, f)
