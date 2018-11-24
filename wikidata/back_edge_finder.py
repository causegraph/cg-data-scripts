#!/usr/bin/env python3

import sys
import json
from collections import Counter

date_path = 'wd_years.json'
rel_path = 'statements_final.txt'
excluded_rels = ['P31', 'P279', 'P61i']
threshold = 1000

if len(sys.argv) > 1:
    threshold = int(sys.argv[1])

with open(date_path) as date_file, open(rel_path) as rel_file:
    dates = json.loads(date_file.read())
    rels = rel_file.read().split('\n')[:-1]

    back_edges = []
    back_edge_ctr = Counter()

    for rel in rels:
        src, type, dest = rel.split()
        if type not in excluded_rels and src in dates and dest in dates:
            d0, d1 = dates[src], dates[dest]
            if d0 > d1 and d0 - d1 > threshold:
                print(src, d0, type, dest, d1)
                back_edge_ctr.update([type])
    print(back_edge_ctr)


