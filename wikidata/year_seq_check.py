#!/usr/bin/env python3
"""check a year sequence to find gaps and anomalies and propose fixes"""

import sys
import time
import json
import urllib.request
import urllib.parse
import zlib

from wd_constants import lang_order

def get_label(obj):
    """get appropriate label, using language fallback chain"""
    has_sitelinks = 'sitelinks' in obj
    for lang in lang_order:
        site = lang + 'wiki'
        if has_sitelinks and site in obj['sitelinks']:
            return obj['sitelinks'][site]['title']
        elif lang in obj['labels']:
            return obj['labels'][lang]['value']
    return None

def get_description(obj):
    try:
        return obj['descriptions']['en']['value']
    except Exception:
        return ''

current_year = 2025

year_seqs = json.loads(open('years_auto.json').read())

seq_to_check = 'france2'

start_id = year_seqs[seq_to_check]['start_id']
end_id = year_seqs[seq_to_check]['end_id']
start_year = year_seqs[seq_to_check]['start_year']
end_year = year_seqs[seq_to_check]['end_year']
search_query = year_seqs[seq_to_check]['search_query']


wd_url = 'https://wikidata.org/wiki/'
skipchars = len(wd_url)
# the API URL to get detailed info on multiple items from Wikidata
url_base = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids='
search_url_base = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search='
# the documented limit on how many items can be queried at once
query_limit = 50

def get_entities(query_ids):
    ids_joined = '|'.join(query_ids)
    req = urllib.request.Request(url_base + ids_joined)
    req.add_header('User-Agent', 'YearSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    # req.add_header('Accept-Encoding', 'gzip')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_json = json.loads(result.read())
    if result_json['success'] == 1:
        return result_json['entities']
    else:
        raise Exception('wbgetentities call failed')

def search_year_item(year, label_query):
    url = search_url_base + urllib.parse.quote(label_query['prefix']) + \
        str(year) + urllib.parse.quote(label_query['suffix']) + \
        "&language=" + label_query['lang']
    print(url)
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'YearSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_content = result.read()
    print(result_content)
    result_json = json.loads(result_content)
    print(result_json)
    return result_json

def check_years(ys):
    search_results = []
    search_entities = {}

    for i in range(ys['start_year'], ys['end_year'] + 1):
        search_results.append(search_year_item(i, ys['search_query']))

    for result in search_results:
        if(len(result['search'])) == 1:
            cur_id = result['search'][0]['id']
            search_entities.update(get_entities([cur_id]))
        elif len(result['search']) > 1:
            print('!!!!danger on', result['search'])

    print('dates to add, if applicable:')
    print('qid,P585')

    for entity in search_entities:
        if 'P585' not in search_entities[entity]['claims']:
            if ys['search_query']['suffix'] != '':
                print(entity + ',+' + get_label(search_entities[entity]).split()[0].strip('.') + '-01-01T00:00:00Z/9')
            elif ys['search_query']['prefix'] != '':
                print(entity + ',+' + get_label(search_entities[entity]).split()[-1] + '-01-01T00:00:00Z/9')

    print('"instance of"/types to add, if applicable:')
    print('qid,P31')

    for entity in search_entities:
        if 'P31' not in search_entities[entity]['claims']:
            print(entity + ',Q18340514')


entities_full = {}

entities_full.update(get_entities([start_id]))
count = 1
next_id = start_id

print('starting at the beginning of the chain')
while True:
    try:
        next_id = entities_full[next_id]['claims']['P156'][0]['mainsnak']['datavalue']['value']['id']
        entities_full.update(get_entities([next_id]))
        count += 1
        item_label = get_label(entities_full[next_id])
        print(count, next_id, item_label, '\t', get_description(entities_full[next_id]))
    except Exception as e:
        print(e)
        print('first gap starts at', next_id)
        gap_start = next_id
        if 'P585' in entities_full[next_id]['claims']:
            gap_start_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        else:
            gap_start_year = start_year
            check_years(year_seqs[seq_to_check])
        print(gap_start)
        break


entities_full.update(get_entities([end_id]))
count = 1
next_id = end_id

print('starting at the end of the chain')
while True:
    try:
        next_id = entities_full[next_id]['claims']['P155'][0]['mainsnak']['datavalue']['value']['id']
        entities_full.update(get_entities([next_id]))
        count += 1
        item_label = get_label(entities_full[next_id])
        print(count, next_id, item_label, '\t', get_description(entities_full[next_id]))
    except Exception as e:
        print(e)
        print('last gap ends at', next_id)
        gap_end = next_id
        if 'P585' in entities_full[next_id]['claims']:
            gap_end_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        else:
            gap_end_year = end_year
            check_years(year_seqs[seq_to_check])
        print(gap_end)
        break

with open('seq_entities_full.json', 'w') as efile:
    json.dump(entities_full, efile, indent=4)

search_results = []

print('checking the gaps')
if gap_start_year < gap_end_year:
    for y in range(gap_start_year - 1, gap_end_year + 1):
        search_results.append(search_year_item(y, search_query))
        time.sleep(0.2)

with open('gap_search_results.json', 'w') as gapfile:
    json.dump(search_results, gapfile, indent=4)

ids = []

for result in search_results:
    search = result['search']
    if len(search) == 1:
        result_id = search[0]['id']
        ids.append(result_id)
        if result_id not in entities_full:
            entities_full.update(get_entities([result_id]))
            time.sleep(0.1)
    elif len(search) == 0:
        print('no results for', result)
    elif len(search) > 1:
        print('multiple results for', result)
        for r in search:
            orig_query = result['searchinfo']['search']
            if r['display']['label']['value'] == orig_query:
                result_id = search[0]['id']
                ids.append(result_id)
                if result_id not in entities_full:
                    entities_full.update(get_entities([result_id]))
                    time.sleep(0.1)


def check_stmt(src, dst, typ):
    try:
        to_check = entities_full[src]['claims'][typ][0]['mainsnak']['datavalue']['value']['id']
    except KeyError as e:
        print('KeyError')
        return False
    if to_check == dst:
        print('TRUE TRUE')
        return True
    else:
        print('FALSE!!!!!!!')
        return False

def is_consecutive(src, dst, typ):
    try:
        src_item = entities_full[src]
        dst_item = entities_full[dst]
        src_year = int(src_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        dst_year = int(dst_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        if typ == 'P155' and dst_year == src_year - 1:
            return True
        elif typ == 'P156' and dst_year == src_year + 1:
            return True
        else:
            return False
    except KeyError:
        return False

prev_statements = ['qid,P155\n']
next_statements = ['qid,P156\n']

for i, id in enumerate(ids):
    if i !=0:
        prev_present = check_stmt(id, ids[i-1], 'P155')
        is_consec = is_consecutive(id, ids[i-1], 'P155')
        if not prev_present and is_consec:
            prev_statements.append(id + ',' + ids[i-1] + '\n')
        else:
            print('statement present:', id, ids[i-1], 'P155')

    if i != len(ids) - 1:
        next_present = check_stmt(id, ids[i+1], 'P156')
        is_consec = is_consecutive(id, ids[i+1], 'P156')
        if not next_present and is_consec:
            next_statements.append(id + ',' + ids[i+1] + '\n')
        else:
            print('statement present:', id, ids[i+1], 'P156')

print(''.join(prev_statements))
print(''.join(next_statements))

with open('seqpatch_' + seq_to_check + '.csv', 'w') as qsfile:
    qsfile.writelines(prev_statements)
    qsfile.writelines(next_statements)
