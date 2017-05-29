#!/usr/bin/python

import networkx
from Bio import Phylo
from networkx.drawing.nx_pydot import write_dot

tree = Phylo.read(
    'opentree9.1_tree/labelled_supertree/labelled_supertree_ottnames.tre',
    'newick')
nxt = Phylo.to_networkx(tree)
write_dot(nxt, 'opentree.dot')
