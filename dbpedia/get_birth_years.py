# extract names and birth years from dbpedia data

from rdflib import Graph
g = Graph()
g.parse('dbpedia_birth_years.nt', format='nt')

date_dict = {}
for stmt in g.subject_objects(URIRef("http://dbpedia.org/ontology/birthYear")):
    date_dict[str(stmt[0])[28:]] = stmt[1]

with open('birth_years.json', 'w') as outfile:
    json.dump(date_dict, outfile)
