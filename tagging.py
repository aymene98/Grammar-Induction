import nltk
import re
import pickle
from reading_collection import get_corpus, get_sentences_word_pos
from corpus_utils import retrieve_corpus_sen_pos_tags


def tagger(taged_sents):
    t0 = nltk.DefaultTagger('NN')
    t1 = nltk.UnigramTagger(taged_sents, backoff=t0)
    t2 = nltk.BigramTagger(taged_sents, backoff=t1)
    t3 = nltk.NgramTagger(3, taged_sents, backoff=t2)
    t4 = nltk.NgramTagger(4, taged_sents, backoff=t3)
    return t4


def create_tagger():
    word_pos_sentences = retrieve_corpus_sen_pos_tags(
        'brown/', remove_tokens=False, universal=True)
    t = tagger(word_pos_sentences)
    pickle.dump(t, open("tagger_universal.p", "wb"))


def tag(sent):
    tagger = pickle.load(open("tagger.p", "rb"))
    l = re.findall(r"[\w']+|[.,!?;]", sent)
    return tagger.tag(l)


def pos_tags(sent):
    return [t[1] for t in tag(sent)]


#l = pos_tags('Hello, my name is aymene.')
# create_tagger()
