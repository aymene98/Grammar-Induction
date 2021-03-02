import nltk

sents = nltk.corpus.brown.sents(categories='news')[:5]

for sent in sents: 
    print(" ".join(sent))