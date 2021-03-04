import nltk

"""sents = nltk.corpus.brown.sents(categories='news')[:5]

for sent in sents: 
    print(" ".join(sent))"""


print(open('./rules.txt', "r", encoding="utf-8").read())

bigram = nltk.bigrams()
dic = nltk.FreqDist(bigram)

bi = nltk.bigrams(test_sent)
for gram in bi:
    dic[gram]/dic.N()