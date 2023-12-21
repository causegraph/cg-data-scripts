#!/usr/bin/env python3
"""analyze, filter, and prioritize back edges results"""

import sys
import time
import json
import urllib.request
import zlib

from collections import Counter

wd_url = 'https://wikidata.org/wiki/'
skipchars = len(wd_url)
# the API URL to get detailed info on multiple items from Wikidata
url_base = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids='
# the documented limit on how many items can be queried at once
query_limit = 50

#use date precision to decide whether some back edges might not mean anything

#group nodes by how many back edges they're involved in

#find the specific date claim responsible and examine its age and/or sources?

#score nodes by how important they are

#get data on which properties have a higher incidence of apparent back edges,
#to understand better what might be going on with them

#date of invention or discovery might mean that a thing existed before "discovery"

def get_entities(query_ids):
    ids_joined = '|'.join(query_ids)
    req = urllib.request.Request(url_base + ids_joined)
    req.add_header('User-Agent', 'BackEdgeAnalyzer/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    # req.add_header('Accept-Encoding', 'gzip')
    result = urllib.request.urlopen(req)
    result_json = json.loads(result.read())
    if result_json['success'] == 1:
        return result_json['entities']
    else:
        raise Exception('wbgetentities call failed')

be_items = Counter()

if len(sys.argv) > 1:
    with open(sys.argv[1]) as be_file:
        for line in be_file:
            ss = line.strip().split()
            if len(ss) == 5 and ss[0].startswith(wd_url) and ss[3].startswith(wd_url):
                be_items.update((ss[0][skipchars:], ss[3][skipchars:]))

        entities = [i[0] for i in be_items.most_common()]
        entity_groups = [entities[i:i+50] for i in range(0, len(entities), 50)]


        print(len(be_items))
        print(entity_groups[0])
        print(len(entity_groups), "entity groups")
        # for group in entity_groups:
        #     print(len(group))

        entities_full = {}
        for eg in entity_groups:
            entities_full.update(get_entities(eg))
            time.sleep(1)

        with open('entities_full.json', 'w') as efile:
            json.dump(entities_full, efile, indent=4)
