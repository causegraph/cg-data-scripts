#!/usr/bin/env python3
"""check the ends of a year sequence to find proposed extensions"""

import time
import json
import urllib.request
import urllib.parse

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
    req.add_header('User-Agent', 'YearSequenceExtender/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_content = result.read()
    # print(result_content)
    result_json = json.loads(result_content)
    # print(result_json)
    return result_json

year_seqs = json.loads(open('years.json').read())
p155s = []
p156s = []


for ys in year_seqs:
    seq = year_seqs[ys]

    entities = {}

    next_year = seq['end_year'] + 1
    search_results = search_year_item(next_year, seq['search_query'])

    print(search_results)

    if(len(search_results['search'])) == 1:
        cur_id = search_results['search'][0]['id']
        entities.update(get_entities([seq['end_id'], cur_id]))
        try:
            end_len = len(entities[seq['end_id']]['labels']['en']['value'])
            cur_len = len(entities[cur_id]['labels']['en']['value'])
            labels_same_length = end_len == cur_len
        except Exception as e:
            print('EXCEPTION:', e)
            labels_same_length = False
        if 'P155' not in entities[cur_id]['claims'] and labels_same_length:
            p155s.append([cur_id,seq['end_id']])
        if 'P156' not in entities[seq['end_id']]['claims'] and labels_same_length:
            p156s.append([seq['end_id'], cur_id])

    elif len(search_results['search']) > 1:
        print('!!!!danger on', search_results['search'])

    prev_year = seq['start_year'] - 1
    search_results = search_year_item(prev_year, seq['search_query'])

    print(search_results)

    if(len(search_results['search'])) == 1:
        cur_id = search_results['search'][0]['id']
        entities.update(get_entities([seq['start_id'], cur_id]))
        try:
            start_len = len(entities[cur_id]['labels']['en']['value'])
            cur_len = len(entities[seq['start_id']]['labels']['en']['value'])
            labels_same_length = start_len == cur_len
        except Exception as e:
            print('EXCEPTION:', e)
            labels_same_length = False
        if 'P155' not in entities[seq['start_id']]['claims'] and labels_same_length:
            p155s.append([seq['start_id'], cur_id])
        if 'P156' not in entities[cur_id]['claims'] and labels_same_length:
            p156s.append([cur_id, seq['start_id']])

    elif len(search_results['search']) > 1:
        print('!!!!danger on', search_results['search'])

print('qid,P155')
for p in p155s:
    print(p[0] + ',' + p[1])

print('qid,P156')
for p in p156s:
    print(p[0] + ',' + p[1])