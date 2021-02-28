import nltk, re, pickle
from reading_collection import get_corpus, get_sentences_word_pos

def tagger(taged_sents):
    t0 = nltk.DefaultTagger('NN')
    t1 = nltk.UnigramTagger(taged_sents, backoff=t0)
    t2 = nltk.BigramTagger(taged_sents, backoff=t1)
    t3 = nltk.NgramTagger(3, taged_sents, backoff=t2)
    t4 = nltk.NgramTagger(4, taged_sents, backoff=t3)
    return t4

def create_tagger():
    corpus = get_corpus(number_of_files=1000)
    word_pos_sentences = get_sentences_word_pos(corpus)
    t = tagger(word_pos_sentences)
    pickle.dump(t, open( "tagger.p", "wb"))
    
    #sent = 'Hello, my name is aymene.'
    #l = re.findall(r"[\w']+|[.,!?;]", sent)
    #print("itwearks x)",t.tag(l))

def tag(sent):
    tagger = pickle.load(open("tagger.p", "rb"))
    l = re.findall(r"[\w']+|[.,!?;]", sent)
    return tagger.tag(l)

def pos_tags(sent):
    return [t[1] for t in tag(sent)]
    
#l = pos_tags('Hello, my name is aymene.')
