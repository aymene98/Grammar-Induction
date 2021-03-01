from os import listdir
import re
import nltk
from nltk import ngrams
from nltk import FreqDist

def get_corpus(number_of_files=5):
    folder = "../brown/brown/"
    file_names = [file for file in listdir(folder) if re.match(r'c\w\d\d', file)]

    corpus = ""
    for name in file_names:
        corpus+= open(folder+name, "r").read()
    
    return corpus

def get_sentences_word_pos(corpus):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = [sentence for sentence in sent_detector.tokenize(corpus)]

    sent_tuple_word_POS_tags = []
    for sentence in sentences:
        sent_tuple_word_POS_tags.append([nltk.tag.str2tuple(word) for word in sentence.split()])

    return sent_tuple_word_POS_tags

def get_pos_tag_sentences(sent_tuple_word_POS_tags):
    sent_POS_tags = []
    for sentence in sent_tuple_word_POS_tags:
        sent_POS_tags.append([word[1] for word in sentence])
    return sent_POS_tags

def main_algorithm(sent_POS_tags):
    # ngrams extraction
    i=0
    rules = ''
    while True:
        NT_name = 'NT'+str(i) # initalizing the name of the non terminal
        fd = nltk.FreqDist() 
        # getting frequency of ngrams of pos-tags; we chose to use 2-grams ... 6-grams
        for gram_length in range(2,7):
            for sentence in sent_POS_tags:
                for gram in list(ngrams(sentence, gram_length)):
                    fd[gram]+=1
        # getting the most frequent pos-tag ngram
        best = fd.most_common(1)[0]
        print("best POS-tag ngram at epoch",i," is :", best)
        # creating a rule for this ngram
        rules += NT_name + ' ==> ' + ' '.join(list(best[0])) + '\n'
        # replacing special caracters in the POS-tag (for regex substitution)
        pattern = re.sub(r'\$', '\$', ' '.join(list(best[0])))
        pattern = re.sub(r'\*', '\*', pattern)
        pattern = re.sub(r'\)', '\)', pattern)
        pattern = re.sub(r'\(', '\(', pattern)
        pattern = re.sub(r'\+', '\+', pattern)
        temp = []
        # substitute all occurences of the most frequent pos-tag ngram by it's NT
        for sentence in sent_POS_tags:
            sent_before = ' '.join(sentence)
            sent_after = re.sub(pattern, NT_name, sent_before)
            temp.append(sent_after.split())
        sent_POS_tags = temp
        
        i+=1
        if len(fd)==1:
            # last rule
            break
    return rules

def write_grammar(grammar):
    grammar_file = open("grammar.txt", "w")
    grammar_file.write(grammar)
    grammar_file.close()


#corpus = get_corpus(number_of_files=1000)
#word_pos_sentences = get_sentences_word_pos(corpus)
#pos_sentences = get_pos_tag_sentences(word_pos_sentences)
#print(len(pos_sentences))
#max_sentences = 150
#rules = main_algorithm(pos_sentences[:max_sentences])
#print("Grammar")
#print(rules)
#write_grammar(rules)