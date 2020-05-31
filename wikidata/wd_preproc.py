#!/usr/bin/env python3
"""simple initial processing of Wikidata JSON dump"""

import json
import sys


def get_labels(obj, label_langs):
    """get appropriate label(s)"""
    labels = {}
    has_sitelinks = 'sitelinks' in obj
    for lang in label_langs:
        site = lang + 'wiki'
        if has_sitelinks and site in obj['sitelinks']:
            labels[lang] = obj['sitelinks'][site]['title']
    return labels


def check_claims(qid, claim, claim_set):
    spec_stmts = set()
    for spec in claim_set:
        # since we're going through all claims without filtering for cg_rels,
        # make sure that this is the right type of thing
        if spec['mainsnak']['datatype'] == 'wikibase-item':
            if 'id' in spec['mainsnak'].get('datavalue', {}).get('value', {}):
                other_qid = spec['mainsnak']['datavalue']['value']['id']
                # TODO I don't think this can be done with claim types
                # get the IDs in a specific order to avoid duplicates
                #if int(qid[1:]) <= int(other_qid[1:]):
                spec_stmts.add((qid, claim, other_qid))
                #else:
                #    spec_stmts.add((other_qid, claim, qid))
    return spec_stmts


def process_json_line(line, label_langs):
    labels = []
    statements = set()

    # collect statements of interest

    try:
        obj = json.loads(line.rstrip(',\n'))
        qid = obj['id']
        item_labels = get_labels(obj, label_langs)
        if item_labels:
            for lang in item_labels:
                # TODO Is this logic too complicated? Is it what I really want?
                labels.append([lang, item_labels[lang], qid])

        is_item = obj['type'] == 'item' or obj['type'] == 'lexeme'
        if is_item and 'claims' in obj:
            claims = obj['claims']

            for claim in claims:
                statements.update(
                    check_claims(qid, claim, claims[claim]))

    except Exception as e:
        if line != '[\n' and line != ']\n':
            print("*** Exception",
                  type(e), "-", e.message, "on following line:")
            print(line)

    return labels, statements


def write_statements(statements, path):
    """write file containing list of statements/relationships"""
    with open(path, 'w') as csvfile:
        csvfile.writelines(
            [item[0] + ' | ' + item[1] + '\n' for item in statements])


def write_items_json(items, path):
    with open(path, 'w') as itemsfile:
        itemsfile.write(json.dumps(items, indent=True))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dump_path = sys.argv[1]
        source = open(dump_path)
    else:
        source = sys.stdin
        
    label_langs = ('en', 'de', 'fr', 'ru', 'it', 'es', 'pl', 'ja', 'pt', 'ar',
                   'nl', 'sv', 'uk', 'ca', 'tr', 'no', 'fi', 'id', 'vi', 'zh',
                   'he')
        
    with open('wd_statements.txt', 'w') as stmts_file:
        labels_files = {}
        
        for lang in label_langs:
            labels_files[lang] = open('wd_labels_' + lang + '.txt', 'w')
         
        for line in source:
            labels, statements = process_json_line(line, label_langs)
            stmts_file.writelines(
            [' | '.join(item) + '\n' for item in statements])
            # write to file corresponding to language code
            for label in labels:
                labels_files[label[0]].write(' | '.join(label[1:]) + '\n')
                
        for lang in labels_files:
            labels_files[lang].close()
        
    #TODO should I check/grab/decompress/verify the wikidata dump from here?
    #TODO get dates; at the very least, get all the date-related info you use in CG right now

