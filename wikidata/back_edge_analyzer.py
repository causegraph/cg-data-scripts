#!/usr/bin/env python3
"""analyze, filter, and prioritize back edges results"""

import sys
import time
import json
import urllib.request

from collections import Counter

wd_url = 'https://wikidata.org/wiki/'
skipchars = len(wd_url)
# the API URL to get detailed info on multiple items from Wikidata
url_base = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids='
# the documented limit on how many items can be queried at once
query_limit = 50

# ideas for future improvements:
#   -group nodes by how many back edges they're involved in
#   -find the specific date claim responsible and examine its age and/or sources?
#   -score nodes by how important they are
#   -get data on which properties have a higher incidence of apparent back edges,
#       to understand better what might be going on with them
#   -date of invention or discovery might mean that a thing existed before "discovery"
#   -use "sorted" back edge files by date to find longest-lasting and/or re-occurring back edges?


def is_date_bad(claims, year):
    for item in claims:
        for c in claims[item]:
            if c['mainsnak']['datatype'] == 'time' and c['mainsnak']['snaktype'] == 'value':
                time_val = c['mainsnak']['datavalue']['value']['time']
                if int(time_val[:5]) == year:
                    #this is the claim relevant to the back edge
                    precision = c['mainsnak']['datavalue']['value']['precision']
                    if c['rank'] == 'deprecated' or precision < 8:
                        #precision < 8 means century or greater; exclude for now, though this could be more precise
                        return True
    return False


def is_excluded(entities, src_id, dst_id, src_yr, dst_yr):
    """check a back edge to see if it can be excluded based on date (im)precision or deprecation"""
    src, dst = entities[src_id], entities[dst_id]
    if is_date_bad(src['claims'], src_yr) or is_date_bad(dst['claims'], dst_yr):
        return True
    else:
        return False



def get_entities(query_ids):
    ids_joined = '|'.join(query_ids)
    req = urllib.request.Request(url_base + ids_joined)
    req.add_header('User-Agent', 'BackEdgeAnalyzer/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    result = urllib.request.urlopen(req)
    result_json = json.loads(result.read())
    if result_json['success'] == 1:
        return result_json['entities']
    else:
        raise Exception('wbgetentities call failed')

be_items = Counter()
back_edges = []

if len(sys.argv) > 1:
    with open(sys.argv[1]) as be_file:
        for line in be_file:
            ss = line.strip().split()
            if len(ss) == 5 and ss[0].startswith(wd_url) and ss[3].startswith(wd_url):
                be_items.update((ss[0][skipchars:], ss[3][skipchars:]))
                back_edges.append((ss[0][skipchars:], int(ss[1]), ss[2], ss[3][skipchars:], int(ss[4])))

        entities = [i[0] for i in be_items.most_common()]
        entity_groups = [entities[i:i+50] for i in range(0, len(entities), 50)]


        print(len(be_items))
        print(entity_groups[0])
        print(len(entity_groups), "entity groups")
        # for group in entity_groups:
        #     print(len(group))

        entities_full = {}
        # following is for testing (use pre-fetched entities)
        # entities_full = json.load(open('entities_full.json'))
        #TODO re-enable next 5 lines after testing
        for eg in entity_groups:
            entities_full.update(get_entities(eg))
            time.sleep(1)
        with open('entities_full.json', 'w') as efile:
            json.dump(entities_full, efile, indent=4)

        with open('back_edges_filtered.txt', 'w') as ffile, open('back_edges_excluded.txt', 'w') as exfile:
            for be in back_edges:
                excluded = is_excluded(entities_full, be[0], be[3], be[1], be[4])
                line = '\t'.join([be[0], str(be[1]), be[2], be[3], str(be[4])]) + '\n'
                if not excluded:
                    ffile.write(line)
                else:
                    exfile.write(line)
