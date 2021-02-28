import nltk, re, pickle
from reading_collection import get_corpus, get_sentences_word_pos

def tagger(taged_sents):
    t1 = nltk.UnigramTagger(taged_sents)
    t2 = nltk.BigramTagger(taged_sents, backoff=t1)
    t3 = nltk.NgramTagger(3, taged_sents, backoff=t2)
    t4 = nltk.NgramTagger(4, taged_sents, backoff=t3)
    return t4

def create_tagger():
        
    corpus = get_corpus(number_of_files=1000)
    word_pos_sentences = get_sentences_word_pos(corpus)
    tagger = tagger(word_pos_sentences)
    pickle.dump(tagger, open( "tagger.p", "wb"))
    
    sent = 'Hello, my name is aymene.'
    l = re.findall(r"[\w']+|[.,!?;]", sent)
    print("itwearks x)",tagger.tag(l))

def tag(sent):
    tagger = pickle.load(open("tagger.p", "rb"))
    l = re.findall(r"[\w']+|[.,!?;]", sent)
    return tagger.tag(l)
    
print(tag('Hello, my name is aymene.'))
