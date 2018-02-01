#!/usr/bin/env python3
"""Generate graph of fictional/mythical classes from Wikidata JSON dump"""

import sys
import json

import networkx as nx

from wd_constants import lang_order

roots = ('Q24199478', 'Q14897293')
subclass = 'P279'


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


def get_item_rels(subj_id, rel, claims):
    class_inst_stmts = []
    if rel in claims:
        for spec in claims[rel]:
            if 'id' in spec['mainsnak'].get('datavalue', {}).get('value', {}):
                obj_id = spec['mainsnak']['datavalue']['value']['id']
                class_inst_stmts.append((subj_id, rel, obj_id))
    return class_inst_stmts


def process_dump(dump_path):
    statements = []
    labels = {}

    with open(dump_path) as infile:
        infile.readline()
        for line in infile:
            try:
                obj = json.loads(line.rstrip(',\n'))
                qid = obj['id']

                if qid not in labels:
                    obj_label = get_label(obj)
                    if obj_label is not None:
                        labels[qid] = obj_label

                if obj['type'] == 'item':
                    statements += get_item_rels(qid, subclass, obj['claims'])
            except Exception as e:
                print('Exception on', qid, '-', e)

    return statements, labels


def graph_from_statements(statements):
    g = nx.DiGraph()
    for line in statements:
        try:
            source = line[0]
            destination = line[2]
            g.add_edge(source, destination)
        except Exception:
            print("error on line:", line)
    return g


def get_all_ancestors(graph, node):
    parents = list(graph.predecessors(node))
    for p in parents:
        parents += get_all_ancestors(graph, p)
    return parents


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dump_path = sys.argv[1]
    else:
        dump_path = 'latest-all.json'

    statements, labels = process_dump(dump_path)
    print("Dump processed!  Making graph...")
    graph = graph_from_statements(statements)
    print("Graph created with", graph.number_of_nodes(), "nodes and",
          graph.number_of_edges(), "edges.")
    to_filter = list(roots)

    for root in roots:
        to_filter += get_all_ancestors(graph, root)

    filter_set = set(to_filter)
    print(len(filter_set), "items in the new filter.")

    filter_dict = {item: labels.get(item, item) for item in filter_set}

    with open("filter.json", 'w') as filterfile:
        filterfile.write(json.dumps(filter_dict, indent=4))
