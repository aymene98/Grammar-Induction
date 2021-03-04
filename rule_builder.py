import json
import nltk
import os
import re

from corpus_utils import retrieve_corpus_sen_pos_tags


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


def rules_to_str(rules):
    content = ''
    nt_rules = []
    for (k, v) in rules.items():
        nt_rules.append(k)
        content += '%s -> %s\n' % (k, ' '.join(
            [t if re.match('NT\d+', t) else '"'+t+'"' for t in v]))
    content = 'S -> %s\n%s' % (" | ".join(nt_rules), content)
    return content


def write_to_txt(str_rules, save_dir, name):
    path = save_dir+name+'.txt'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str_rules)


def checkpoint(counter, sen_pos_tags, rules, dir):
    save = {'counter': counter, 'sen_pos_tags': sen_pos_tags, 'rules': rules}
    with open(dir+'checkpoint.json', 'w', encoding='utf-8') as f:
        json.dump(save, f, ensure_ascii=False, indent=4)


def split(in_list, train_percent=70):
    train_size = round(train_percent * len(in_list) / 100)
    return in_list[:train_size], in_list[train_size:]


def build_rules(sen_pos_tags, name, checkpoint_interval=2000, save_dir=''):
    counter = 0
    rules = {}

    # prepare checkpoint dir, load save if possible
    dir = save_dir + 'checkpoint/'
    if not os.path.exists(dir):
        os.mkdir(dir)
    elif os.path.exists(dir+'checkpoint.json'):
        with open(dir+'checkpoint.json', 'r', encoding='utf-8') as f:
            save = json.load(f)
            counter = save['counter'] + 1
            rules = save['rules']
            sen_pos_tags = save['sen_pos_tags']

    while True:
        rule = 'NT%d' % counter
        fd = nltk.FreqDist()

        # compute n-gram frequencies
        for pos_tags in sen_pos_tags:
            for gram_len in range(2, len(pos_tags)):
                # for gram_len in range(2, 7):
                for gram in nltk.ngrams(pos_tags, gram_len):
                    fd[gram] += 1

        fd_len = len(fd)
        print('fd_len: ', fd_len, 'counter: ',  counter)

        if fd_len == 0:
            break

        # update rules
        pos_tag = fd.most_common(1)[0][0]
        rules[rule] = pos_tag

        # replace the most frequent n-gram by the generated rule
        i = 0
        for i in range(len(sen_pos_tags)):
            sen_pos_tags[i] = replace_pos_tag(sen_pos_tags[i], pos_tag, rule)

        if counter != 0 and counter % checkpoint_interval == 0:
            checkpoint(counter, sen_pos_tags, rules, dir)

        counter += 1

    str_rules = rules_to_str(rules)
    write_to_txt(str_rules, save_dir, name)
    return str_rules


# sen_pos_tags = retrieve_corpus_sen_pos_tags('brown/', 0.7, simplify_tags=True)

# print(len(sen_pos_tags))
# train_set, _ = split(sen_pos_tags)
# build_rules(sen_pos_tags, checkpoint_interval=100)

# with open('checkpoint/checkpoint.json', 'r') as f:
#     save = json.load(f)
#     rules = save['rules']
#     counter = save['counter']
#     str_rules = rules_to_str(rules, counter)
#     write_to_txt(str_rules, '')

# with open('rules.txt') as f:
#     print(f.read())


# The Fulton County Grand Jury said Friday an investigation of Atlanta's recent primary election produced `` no evidence '' that any irregularities took place
