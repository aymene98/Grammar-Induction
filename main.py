import nltk
import re
import os
import json


def read_corpus(uri, limit=5):
    filenames = [f for f in os.listdir(uri) if re.match('c[a-z]\d{2}', f)]
    corpora = []
    for fn in filenames[:limit]:
        with open(uri+fn, 'r', encoding='utf-8') as f:
            corpora.append(f.read())
    return "".join(corpora)


def retrieve_sen_pos_tags(corpus):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(corpus)
    return [re.findall('.+?/(.+?)(?: |$)', s) for s in sentences]


def replace_pos_tag(pos_tags, to_replace, rule):
    j = 0
    replacement = []
    for i in range(len(pos_tags)):
        if pos_tags[i] != to_replace[j]:
            for k in range(i-j, i+1):
                replacement.append(pos_tags[k])
            j = 0
        else:
            if j == len(to_replace) - 1:
                replacement.append(rule)
                j = 0
            else:
                j += 1
    return replacement


def write_to_json(rules):
    with open('out.json', 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)


def write_to_txt(rules):
    content = ''
    for (k, v) in rules.items():
        content += '%s ==> %s\n' % (k, str(v))
    with open('out.txt', 'w', encoding='utf-8') as f:
        f.write(content)


def run_thingy(sen_pos_tags):
    counter = 0
    rules = {}
    while True:
        rule = 'NT%d' % counter
        fd = nltk.FreqDist()

        # compute n-gram frequencies
        for pos_tags in sen_pos_tags:
            for gram_len in range(2, len(pos_tags)):
                for gram in nltk.ngrams(pos_tags, gram_len):
                    fd[gram] += 1

        if len(fd) == 0:
            break

        # update rules
        pos_tag = fd.most_common(1)[0][0]
        rules[rule] = pos_tag

        # replace the most frequent n-gram by the generated rule
        i = 0
        for i in range(len(sen_pos_tags)):
            sen_pos_tags[i] = replace_pos_tag(sen_pos_tags[i], pos_tag, rule)

        counter += 1

    return rules


corpus = read_corpus('brown/')
sen_pos_tags = retrieve_sen_pos_tags(corpus)
rules = run_thingy(sen_pos_tags[:150])
write_to_json(rules)
