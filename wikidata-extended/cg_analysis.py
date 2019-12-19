#!/usr/bin/env python3

import json
import networkx as nx

wd_url = 'https://wikidata.org/wiki/'

cg = nx.read_graphml('nxcg.graphml')

years = json.loads(open('wd_years.json').read())

maxdeg = 1
degrees = cg.degree()

#TODO fix this
#for n in degrees:
#    if n[1] >= maxdeg and n[0] not in years:
#        print(n)
#        maxdeg = n[1]

cg_dg = nx.DiGraph(cg)

pr = nx.pagerank(cg_dg)
maxpr = 0

for n in pr:
    if pr[n] >= maxpr and n not in years:
        print(wd_url + n, pr[n])
        maxpr = pr[n]
