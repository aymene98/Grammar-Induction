from os import listdir
import re
import nltk
from nltk import ngrams
from nltk import FreqDist

folder = "../brown/brown/"
file_names = [file for file in listdir(folder) if re.match(r'c\w\d\d', file)]

corpus = ""
for name in file_names[:10]:
    corpus+= open(folder+name, "r").read()

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

sentences = [sentence for sentence in sent_detector.tokenize(corpus)]

sent_tuple_word_POS_tags = []
for sentence in sentences:
    sent_tuple_word_POS_tags.append([nltk.tag.str2tuple(word) for word in sentence.split()])

#print(len(sent_tuple_word_POS_tags[0]))
#[print(x) for x in sent_tuple_word_POS_tags[:10]]

sent_POS_tags = []
for sentence in sent_tuple_word_POS_tags:
    sent_POS_tags.append([word[1] for word in sentence])

sent_POS_tags = sent_POS_tags[:150]

# ngrams extraction
i=0
rules = ''
while True:
    NT_name = 'NT'+str(i)
    fd = nltk.FreqDist()
    for gram_length in range(2,7):
        for sentence in sent_POS_tags:
            for gram in list(ngrams(sentence, gram_length)):
                fd[gram]+=1
    best = fd.most_common(1)[0]
    print("best ngram at epoch",i," is :", best)
    rules += NT_name + ' ==> ' + ' '.join(list(best[0])) + '\n'
    #print(list(best[0]))
    #substitute all occurances of best in the sent_POS_tags
    pattern = re.sub(r'\$', '\$', ' '.join(list(best[0])))
    pattern = re.sub(r'\*', '\*', pattern)
    pattern = re.sub(r'\)', '\)', pattern)
    pattern = re.sub(r'\(', '\(', pattern)
    pattern = re.sub(r'\+', '\+', pattern)
    #print(pattern)
    temp = []
    for sentence in sent_POS_tags:
        sent_before = ' '.join(sentence)
        sent_after = re.sub(pattern, NT_name, sent_before)
        #if len(sent_before) != len(sent_after):
        #    print("change")
        temp.append(sent_after.split())

    sent_POS_tags = temp
    i+=1
    if len(fd)==1:
        # last rule
        break

print("Grammar")
print(rules)
