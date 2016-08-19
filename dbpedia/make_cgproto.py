import networkx as nx

ntriples = open("dbpedia_influences.nt", 'r')

# an influence graph is a directed graph
g = nx.DiGraph()

# parse the n-triples and add the nodes and edges to our graph
for ntriple in ntriples:
    splitup = ntriple.strip('\t\n .').split()
    node1, node2 = splitup[0].strip('<>'), splitup[2].strip('<>')
    if not g.has_node(node1):
        g.add_node(node1)
    if not g.has_node(node2):
        g.add_node(node2)
    if splitup[1] == '<http://dbpedia.org/ontology/influencedBy>':
        g.add_edge(node2, node1)
    else:
        g.add_edge(node1, node2)

# networkx can also write other formats, e.g. GraphML
nx.write_dot(g, "influences.dot")
