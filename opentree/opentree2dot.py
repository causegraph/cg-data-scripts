#!/usr/bin/python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import networkx
from Bio import Phylo
from networkx.drawing.nx_pydot import write_dot

tree = Phylo.read('opentree9.1_tree/labelled_supertree/labelled_supertree.tre',
                  'newick')
nxt = Phylo.to_networkx(tree)
# warning: this next line may require a substantial amount of memory
write_dot(nxt, 'opentree.dot')
