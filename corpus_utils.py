import nltk
import os
import re
import xml.etree.ElementTree as ET

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def retrieve_corpus_sen_pos_tags(corpus_dir, sen_limit=None, remove_tokens=True, simplify_tags=False, universal=False):
    uris = [corpus_dir+fn for fn in os.listdir(corpus_dir)]
    sen_pos_tags = []
    for file_uri in uris:
        if file_uri.endswith('.xml'):
            # parsing xml file
            sen_pos_tags.extend(_get_pos_tags_from_xml(file_uri))
        else:
            with open(file_uri, 'r', encoding='utf-8')as f:
                content = f.read()
                if re.match('\s*(?:(?:.+?)\/(?:.+?)(?:\s+|$))+', content):
                    # valid corpus
                    sen_pos_tags.extend(_get_pos_tags_from_str(content))
    if sen_limit:
        sen_pos_tags = sen_pos_tags[:int(sen_limit*len(sen_pos_tags))]
    for i in range(len(sen_pos_tags)):
        # transform NN-TL, JJ-TL to NN, JJ...
        if simplify_tags:
            sen_pos_tags[i] = _simplify_tokens(sen_pos_tags[i])
        # transform to universal tags (NN -> NOUN, JJ -> ADJ...)
        if universal:
            sen_pos_tags[i] = _to_universal_pos_tags(sen_pos_tags[i])
        # only keep tags
        if remove_tokens:
            sen_pos_tags[i] = _remove_tokens(sen_pos_tags[i])

    return sen_pos_tags


def _get_pos_tags_from_str(corpus_content):
    sentences = sent_detector.tokenize(corpus_content)
    sen_pos_tags = []
    for s in sentences:
        pos_tags = re.findall('\s*(.+?/.+?)(?:\s|$)', s)
        if len(pos_tags) > 1:
            pos_tags = [nltk.tag.str2tuple(pos_tag) for pos_tag in pos_tags]
            pos_tags = [(token, tag.upper()) for (token, tag) in pos_tags]
            sen_pos_tags.append(pos_tags)
    return sen_pos_tags


def _get_pos_tags_from_xml(file_uri):
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
                    pos_tags.append((e.text, tag))
            if len(pos_tags) > 1:
                sen_pos_tags.append(pos_tags)
    return sen_pos_tags


def _simplify_tokens(pos_tags):
    return [(token, re.sub('(-\w+)+', '', tag)) for (token, tag) in pos_tags]


def _to_universal_pos_tags(pos_tags):
    tokens, tags = zip(*pos_tags)
    tags = list(tags)
    tagged_tokens = nltk.tag.pos_tag(tokens)
    for i in range(len(tags)):
        tag = nltk.tag.map_tag('en-ptb', 'universal', tags[i])
        if tag == 'X':
            tag = nltk.tag.map_tag('en-ptb', 'universal', tagged_tokens[i][1])
        tags[i] = tag
    return list(zip(tokens, tags))


def _remove_tokens(pos_tags):
    return [tag for (_, tag) in pos_tags]
