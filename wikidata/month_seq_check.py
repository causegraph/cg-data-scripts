#!/usr/bin/env python3
"""check a month sequence to find gaps and anomalies and propose fixes"""

import sys
import time
import json
import urllib.request
import urllib.parse
import zlib

from wd_constants import lang_order

# different languages?  use WD?  generate multilingual list once from WD?
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

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

current_month = '2025-05'

month_seqs = json.loads(open('months.json').read())

seq_to_check = 'united_states'

start_id = month_seqs[seq_to_check]['start_id']
end_id = month_seqs[seq_to_check]['end_id']
start_month = month_seqs[seq_to_check]['start_month']
end_month = month_seqs[seq_to_check]['end_month']
search_query = month_seqs[seq_to_check]['search_query']


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
    req.add_header('User-Agent', 'MonthSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    # req.add_header('Accept-Encoding', 'gzip')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_json = json.loads(result.read())
    if result_json['success'] == 1:
        return result_json['entities']
    else:
        raise Exception('wbgetentities call failed')

def search_month_item(month, label_query):
    url = search_url_base + urllib.parse.quote(label_query['prefix']) + \
        urllib.parse.quote(month) + urllib.parse.quote(label_query['suffix']) + \
        "&language=" + label_query['lang']
    print(url)
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'MonthSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_content = result.read()
    print(result_content)
    result_json = json.loads(result_content)
    print(result_json)
    return result_json

def next_month(month):
    s = month.split()
    if len(s) == 2 and s[0] in months: 
        if s[0] == 'December':
            return 'January ' + str(int(s[1]) + 1)
        else:
            return months[months.index(s[0]) + 1] + ' ' + s[1]
        
def prev_month(month):
    s = month.split()
    if len(s) == 2 and s[0] in months: 
        if s[0] == 'January':
            return 'December ' + str(int(s[1]) - 1)
        else:
            return months[months.index(s[0]) - 1] + ' ' + s[1]
        
def month_range(start_month, end_month):
    result = []
    current_month = start_month
    while current_month != end_month:
        result.append(current_month)
        current_month = next_month(current_month)
    return result

def check_months(ys):
    search_results = []
    search_entities = {}

    for i in month_range(ys['start_month'], next_month(ys['end_month'])):
        search_results.append(search_month_item(i, ys['search_query']))

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
                print(entity + ',+' + dewordify_month(get_label(search_entities[entity]).split()[0].strip('.')) + '-01T00:00:00Z/9')
            elif ys['search_query']['prefix'] != '':
                print(entity + ',+' + dewordify_month(get_label(search_entities[entity]).split()[-1]) + '-01T00:00:00Z/9')

    print('"instance of"/types to add, if applicable:')
    print('qid,P31')

    for entity in search_entities:
        if 'P31' not in search_entities[entity]['claims']:
            print(entity + ',Q18340514')


entities_full = {}

entities_full.update(get_entities([start_id]))
count = 1
next_id = start_id

def wordify_month(month):
    """convert e.g. '1987-07' to 'July 1987'"""
    s = month.split('-')
    if len(s) == 2 and 0 < int(s[1]) < 13:
        return months[int(s[1]) - 1] + ' ' + s[0]
    else:
        raise Exception('improper month expression', month)
    
def dewordify_month(month):
    """convert e.g. 'July 1987' to '1987-07'"""
    s = month.split()
    if len(s) == 2 and s[0] in months:
        return s[1] + '-' + months[months.index(s[1]) + 1]
    else:
        raise Exception('improper month expression', month)

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
            gap_start_month = wordify_month(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:8])
            print('if - gap_start_month now set to', gap_start_month)
        else:
            gap_start_month = start_month
            print('else - gap_start_month now set to', gap_start_month)
            check_months(month_seqs[seq_to_check])
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
            to_convert = entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:8]
            print('wordifying', to_convert)
            gap_end_month = wordify_month(to_convert)
            print(gap_end_month)
        else:
            print('else wordifying', end_month)
            gap_end_month = end_month # wordify_month(end_month)
            print(gap_end_month)
            check_months(month_seqs[seq_to_check])
        print(gap_end)
        break

with open('seq_entities_full.json', 'w') as efile:
    json.dump(entities_full, efile, indent=4)

search_results = []

def earlier_month(start_month, end_month):
    ss = start_month.split()
    es = end_month.split()
    try:
        if int(es[1]) > int(ss[1]):
            return True
        elif int(es[1]) == int(ss[1]) and months.index(es[0]) > months.index(ss[0]):
            return True
        else:
            return False
    except Exception as e:
        print('error with', ss, 'and', es)


print('checking the gaps')
if earlier_month(gap_start_month, gap_end_month):
    for y in month_range(prev_month(gap_start_month), next_month(gap_end_month)):
        search_results.append(search_month_item(y, search_query))
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
        to_check = ''
        if typ in entities_full[src]['claims']:
            to_check = entities_full[src]['claims'][typ][0]['mainsnak']['datavalue']['value']['id']
    except KeyError as e:
        print('KeyError in check_stmt():', src, dst, typ, e)
        return False
    if to_check == dst:
        # print('check_stmt is True')
        return True
    else:
        # print('check_stmt() is False')
        return False

def is_consecutive(src, dst, typ):
    try:
        src_item = entities_full[src]
        dst_item = entities_full[dst]
        src_month = wordify_month(src_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:8])
        dst_month = wordify_month(dst_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:8])
        if typ == 'P155' and dst_month == prev_month(src_month):
            return True
        elif typ == 'P156' and dst_month == next_month(src_month):
            return True
        else:
            print('is_consecutive() returning non-error False with typ', typ, 'src_month', src_month, 'dst_month', dst_month)
            print(dst_month, 'is neither', prev_month(src_month), 'nor', next_month(src_month))
            return False
    except KeyError:
        print('KeyError in is_consecutive():', src_month, dst_month, typ)
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
            print('is_consec is', is_consec)

    if i != len(ids) - 1:
        next_present = check_stmt(id, ids[i+1], 'P156')
        is_consec = is_consecutive(id, ids[i+1], 'P156')
        if not next_present and is_consec:
            next_statements.append(id + ',' + ids[i+1] + '\n')
        else:
            print('statement present:', id, ids[i+1], 'P156')
            print('is_consec is', is_consec)

print(''.join(prev_statements))
print(''.join(next_statements))

with open('seqpatch_' + seq_to_check + '.csv', 'w') as qsfile:
    qsfile.writelines(prev_statements)
    qsfile.writelines(next_statements)
