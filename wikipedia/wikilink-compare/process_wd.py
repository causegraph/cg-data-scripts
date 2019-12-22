#!/usr/bin/env python3

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
                # get the IDs in a specific order to avoid duplicates
                if int(qid[1:]) <= int(other_qid[1:]):
                    spec_stmts.add((qid, other_qid))  # , claim))
                else:
                    spec_stmts.add((other_qid, qid))  # , claim))
    return spec_stmts


def process_dump(dump_path, label_langs=('en', 'de', 'fr', 'ru', 'it', 'es',
                                         'pl', 'ja', 'pt', 'ar', 'nl', 'sv',
                                         'uk', 'ca', 'tr', 'no', 'fi', 'id',
                                         'vi', 'zh', 'he')):
    labels = {}
    statements = set()

    # TODO remove if not testing
    # item_count = 0
    # test_limit = 10000

    for lang in label_langs:
        labels[lang] = {}

    # collect statements of interest
    with open(dump_path) as infile:
        infile.readline()
        for line in infile:
            # TODO remove if not testing
            # item_count += 1
            # if item_count > test_limit:
            #     break

            try:
                obj = json.loads(line.rstrip(',\n'))
                qid = obj['id']
                item_labels = get_labels(obj, label_langs)
                if item_labels:
                    for lang in item_labels:
                        labels[lang][item_labels[lang]] = qid

                is_item = obj['type'] == 'item' or obj['type'] == 'lexeme'
                if is_item and 'claims' in obj:
                    claims = obj['claims']

                    for claim in claims:
                        statements.update(
                            check_claims(qid, claim, claims[claim]))

            except Exception as e:
                if line != ']\n':
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
    else:
        dump_path = 'latest-all.json'

    labels, statements = process_dump(dump_path)
    write_statements(statements, 'statements.txt')
    write_items_json(labels, 'wd_labels.json')
