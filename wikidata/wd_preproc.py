#!/usr/bin/env python3
"""simple initial processing of Wikidata JSON dump"""

import json
import sys

from wd_constants import all_times


def get_labels(obj, label_langs):
    """
    get appropriate label(s), including multilingual Wikipedia titles
    and a "best" overall human-readable label given the language chain
    """
    labels = {}
    has_sitelinks = 'sitelinks' in obj
    for lang in label_langs:
        site = lang + 'wiki'
        if has_sitelinks and site in obj['sitelinks']:
            labels[lang] = obj['sitelinks'][site]['title']
            if 'best' not in labels:
                labels['best'] = labels[lang]
        elif 'best' not in labels and lang in obj['labels']:
            labels['best'] = obj['labels'][lang]['value']
    if 'best' not in labels:
        labels['best'] = obj['id']

    if 'claims' in obj and 'P356' in obj['claims']:
        try:
            labels['doi'] = obj['claims']['P356'][0]['mainsnak']['datavalue']['value']
        except Exception:
            pass
            # print('No DOI for', obj['id'])

    return labels


def get_date_claims(claims, props=all_times):
    """get date claims in the specified collection of properties"""
    result = []
    for claim in claims:
        if claim in props:
            for spec in claims[claim]:
                if 'time' in spec['mainsnak'].get('datavalue', {}).get(
                        'value', {}):
                    date = spec['mainsnak']['datavalue']['value']['time']
                    result.append([claim, date])
    return result


def check_nested_dates(claim, claim_set):
    result = []
    for spec in claim_set:
        qualifiers = spec.get('qualifiers', {})
        for qualifier in qualifiers:
            if qualifier in all_times:
                for item in qualifiers[qualifier]:
                    if 'time' in item.get('datavalue', {}).get('value', {}):
                        date = item['datavalue']['value']['time']
                        result.append([claim + ' ' + qualifier, date])

    return result


def check_claims(qid, claim, claim_set):
    spec_stmts = dict()
    for spec in claim_set:
        # since we're going through all claims without filtering for cg_rels,
        # make sure that this is the right type of thing
        if spec['mainsnak']['datatype'] == 'wikibase-item':
            if 'id' in spec['mainsnak'].get('datavalue', {}).get('value', {}):
                other_qid = spec['mainsnak']['datavalue']['value']['id']
                # TODO I don't think this can be done with claim types
                # get the IDs in a specific order to avoid duplicates
                #if int(qid[1:]) <= int(other_qid[1:]):
                #spec_stmts.add((qid, claim, other_qid))
                claim_key = qid + other_qid
                if claim_key in spec_stmts and claim not in spec_stmts[claim_key]['wd_types']:
                    spec_stmts[claim_key]['wd_types'].append(claim)
                elif claim_key not in spec_stmts:
                    spec_stmts[claim_key] = {'_key': claim_key, '_from': qid, '_to': other_qid}
                    spec_stmts[claim_key]['wd_types'] = [claim]
                #else:
                #    spec_stmts.add((other_qid, claim, qid))

        #TODO see what this does, and maybe put in its own function
        #and results in their own file
        qualifiers = spec.get('qualifiers', {})
        for qualifier in qualifiers:
            for item in qualifiers[qualifier]:
                if item['datatype'] == 'wikibase-item' and item['snaktype'] == 'value':
                    try:
                        qualifier_id = item['datavalue']['value']['id']
                        claim_key = qid + qualifier_id
                        if claim_key in spec_stmts and qualifier not in spec_stmts[claim_key]['wd_types']:
                            spec_stmts[claim_key]['wd_types'].append(qualifier)
                        elif claim_key not in spec_stmts:
                            spec_stmts[claim_key] = {'_key': claim_key, '_from': qid, '_to': qualifier_id}
                            spec_stmts[claim_key]['wd_types'] = [qualifier]
                    except Exception:
                        print('couldn\'t get ID for:', item)
    return spec_stmts


def process_json_line(line, label_langs):
    qid = None
    labels = {}
    statements = {}
    wp_langs = []

    # collect statements of interest

    obj = json.loads(line.rstrip(',\n'))
    qid = obj['id']
    labels = get_labels(obj, label_langs)

    is_item = obj['type'] == 'item' or obj['type'] == 'lexeme'
    if is_item and 'claims' in obj:
        claims = obj['claims']

        for claim in claims:
            statements.update(
                check_claims(qid, claim, claims[claim]))


    if 'sitelinks' in obj:
        wp_langs = [l[:-4] for l in obj['sitelinks'] if l.endswith('wiki')]

    return qid, labels, statements, wp_langs


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

    # 'doi' is for Digital Object Identifiers; Wikidata has them, and Wikipedia
    #     links to them with links that look very much like inter-language
    #     Wikipedia links
    # 'best' is for the best label that can be found along the language chain
    label_langs = ('en', 'de', 'fr', 'ru', 'it', 'es', 'pl', 'ja', 'pt', 'ar', 'nl', 'sv', 'uk', 'ca', 'tr', 'no', 'fi', 'id', 'vi', 'zh', 'he', 'ceb', 'war', 'fa', 'sr', 'arz', 'ko', 'hu', 'cs', 'sh', 'ro', 'zh_min_nan', 'eu', 'ms', 'eo', 'hy', 'ce', 'bg', 'da', 'azb', 'sk', 'kk', 'min', 'hr', 'et', 'lt', 'be', 'el', 'sl', 'simple', 'gl', 'az', 'ur', 'nn', 'hi', 'th', 'ka', 'uz', 'la', 'cy', 'ta', 'vo', 'ast', 'mk', 'lv', 'tg', 'tt', 'mg', 'af', 'bn', 'oc', 'zh_yue', 'bs', 'sq', 'ky', 'new', 'tl', 'be_x_old', 'te', 'ml', 'br', 'nds', 'pms', 'su', 'sw', 'ht', 'lb', 'vec', 'jv', 'mr', 'sco', 'pnb', 'ga', 'ba', 'szl', 'is', 'my', 'fy', 'cv', 'lmo', 'an', 'pa', 'ne', 'wuu', 'yo', 'bar', 'io', 'ku', 'gu', 'als', 'ckb', 'kn', 'scn', 'bpy', 'ia', 'qu', 'diq', 'mn', 'bat_smg', 'or', 'si', 'nv', 'cdo', 'ilo', 'gd', 'yi', 'am', 'nap', 'bug', 'xmf', 'wa', 'sd', 'hsb', 'mai', 'map_bms', 'fo', 'mzn', 'li', 'eml', 'sah', 'os', 'ps', 'sa', 'frr', 'bcl', 'ace', 'zh_classical', 'mrj', 'mhr', 'hif', 'hak', 'roa_tara', 'pam', 'nso', 'km', 'hyw', 'rue', 'se', 'crh', 'bh', 'shn', 'vls', 'mi', 'nds_nl', 'nah', 'as', 'sc', 'vep', 'gor', 'gan', 'myv', 'ab', 'glk', 'bo', 'so', 'co', 'tk', 'fiu_vro', 'sn', 'lrc', 'kv', 'csb', 'ha', 'gv', 'udm', 'ie', 'ay', 'pcd', 'zea', 'kab', 'nrm', 'ug', 'lez', 'kw', 'stq', 'haw', 'frp', 'lfn', 'lij', 'mwl', 'gn', 'gom', 'rm', 'mt', 'lo', 'lad', 'koi', 'sat', 'fur', 'olo', 'dty', 'dsb', 'ang', 'ext', 'ln', 'bjn', 'ban', 'cbk_zam', 'dv', 'ksh', 'gag', 'pfl', 'tyv', 'pag', 'pi', 'zu', 'av', 'awa', 'bxr', 'xal', 'krc', 'pap', 'za', 'pdc', 'kaa', 'rw', 'arc', 'szy', 'to', 'nov', 'jam', 'tpi', 'kbp', 'kbd', 'ig', 'na', 'tet', 'wo', 'tcy', 'ki', 'inh', 'jbo', 'atj', 'roa_rup', 'bi', 'lbe', 'kg', 'ty', 'mdf', 'lg', 'srn', 'xh', 'gcr', 'fj', 'ltg', 'chr', 'sm', 'ak', 'got', 'kl', 'pih', 'om', 'cu', 'tn', 'tw', 'st', 'ts', 'rmy', 'bm', 'nqo', 'chy', 'rn', 'mnw', 'tum', 'ny', 'ss', 'ch', 'pnt', 'iu', 'ady', 'ks', 've', 'ee', 'ik', 'sg', 'ff', 'ti', 'dz', 'din', 'cr', 'ng', 'cho', 'kj', 'mh', 'ho', 'ii', 'aa', 'mus', 'hz', 'kr', 'smn', 'doi', 'best')

    with open('items.jsonl', 'w') as items_file, \
         open('links.jsonl', 'w') as rels_file, \
         open('wd_labels.txt', 'w') as labels_file:

        #TODO get date working

        # items_file.write('_key\tlabel\n')
        #rels_file.write('_key\t_from\ttype\t_to\n')

        for line in source:
            try:
                qid, labels, statements, wp_langs = process_json_line(line, label_langs)
                items_file.write(json.dumps(
                    {
                     '_key': qid,
                     'label': labels['best'],
                     'wp_langs': wp_langs
                    }) + '\n')
                rels_file.writelines(
                [json.dumps(statements[key]) + '\n' for key in statements])
                label_lines = [lang + '\t' + labels[lang] + '\t' + qid + '\n'
                                for lang in labels]
                labels_file.writelines(label_lines)
            except Exception as e:
                if line != '[\n' and line != ']\n':
                    print("*** Exception:",
                          type(e), "-", e, "on following line:")
                    print(line)


    #TODO should I check/grab/decompress/verify the wikidata dump from here?
    #TODO get dates; at the very least, get all the date-related info you use in CG right now
