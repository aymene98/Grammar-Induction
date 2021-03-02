import json
import nltk
import os
import re
import xml.etree.ElementTree as ET


def retrieve_corpus_sen_pos_tags(corpus_dir, limit=None):
    uris = [corpus_dir+fn for fn in os.listdir(corpus_dir)]
    if not limit:
        limit = len(uris)
    sen_pos_tags = []
    for file_uri in uris[:limit]:
        if file_uri.endswith('.xml'):
            # parsing xml file
            sen_pos_tags.extend(get_pos_tags_from_xml(file_uri))
        else:
            with open(file_uri, 'r', encoding='utf-8')as f:
                content = f.read()
                if re.match('\s*(?:(?:.+?)\/(?:.+?)(?:\s+|$))+', content):
                    # valid corpus
                    sen_pos_tags.extend(get_pos_tags_from_str(content))
    return sen_pos_tags


def get_pos_tags_from_str(corpus_content):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(corpus_content)
    sen_pos_tags = []
    for s in sentences:
        tags = re.findall('.+?/(.+?)(?:\s|$)', s.upper())
        if len(tags) > 1:
            sen_pos_tags.append(tags)
    return sen_pos_tags


def get_pos_tags_from_xml(file_uri):
    tree = ET.parse(file_uri)
    root = tree.getroot()
    body = None
    try:
        body = root[1][0]
    except:
        return []
    sen_pos_tags = []
    for p in body:
        for s in p:
            pos_tags = []
            for e in s:
                tag = None
                if 'type' in e.attrib:
                    tag = e.attrib['type'] if e.attrib['type'] != 'pct' else e.text
                elif 'pos' in e.attrib:
                    tag = e.attrib['pos'].replace(' ', '')
                if tag:
                    pos_tags.append(tag)
            if len(pos_tags) > 1:
                sen_pos_tags.append(pos_tags)
    return sen_pos_tags


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


def rules_to_str(rules, counter):
    content = 'S -> NT%d\n' % counter
    for (k, v) in rules.items():
        content += '%s -> %s\n' % (k, ' '.join(
            [t if re.match('NT\d+', t) else '"'+t+'"' for t in v]))
    return content


def write_to_txt(str_rules, save_dir):
    with open(save_dir+'rules.txt', 'w', encoding='utf-8') as f:
        f.write(str_rules)


def checkpoint(counter, sen_pos_tags, rules, dir):
    save = {'counter': counter, 'sen_pos_tags': sen_pos_tags, 'rules': rules}
    with open(dir+'checkpoint.json', 'w', encoding='utf-8') as f:
        json.dump(save, f, ensure_ascii=False, indent=4)


def split(in_list, train_percent=70):
    train_size = round(train_percent * len(in_list) / 100)
    return in_list[:train_size], in_list[train_size:]


def build_rules(sen_pos_tags, checkpoint_interval=2000, save_dir=''):
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

    str_rules = rules_to_str(rules, counter-1)
    write_to_txt(str_rules, save_dir)
    return str_rules


#sen_pos_tags = retrieve_corpus_sen_pos_tags('brown/')
#train_set, _ = split(sen_pos_tags)
#build_rules(train_set, checkpoint_interval=100)

# with open('checkpoint/checkpoint.json', 'r') as f:
#     save = json.load(f)
#     rules = save['rules']
#     counter = save['counter']
#     str_rules = rules_to_str(rules, counter)
#     write_to_txt(str_rules, '')

# with open('rules.txt') as f:
#     print(f.read())
