#!/usr/bin/python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json

import networkx
from Bio import Phylo
from networkx.drawing.nx_pydot import write_dot

tree = Phylo.read(
    'opentree9.1_tree/labelled_supertree/labelled_supertree_ottnames.tre',
    'newick')
nxt = Phylo.to_networkx(tree)
nodes = nxt.nodes()
labels = {}

for node in nodes:
    if '_' in node.name and ' ' not in node.name:
        ott_id = node.name.rsplit(' ', maxsplit=1)[1]
        labels[ott_id] = node.name.replace('_', ' ').replace('ott', '- ')
    elif ' ' in node.name and '_' not in node.name:
        ott_id = node.name.rsplit(' ', maxsplit=1)[1]
        labels[ott_id] = node.name.replace('ott', '- ')
    elif node.name.startswith('mrcaott'):
        labels[node.name] = node.name.replace('ott', ' - ')
    elif node.name.rsplit(' ', maxsplit=1)[1].startswith('ott'):
        ott_id = node.name.rsplit(' ', maxsplit=1)[1]
        labels[ott_id] = node.name.replace('ott', '- ')
    else:
        print("not sure what to do with this node name:", node.name)

for label in labels:
    if label.startswith('ott'):
        try:
            int(label[3:])
        except Exception:
            print("issue with label:", label, labels[label])
    elif not label.startswith('mrcaott'):
        print("issue with label:", label, labels[label])

with open('full_labels.json', 'w') as labelsfile:
    labelsfile.write(json.dumps(labels))
