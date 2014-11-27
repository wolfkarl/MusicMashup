import rdflib

g = rdflib.Graph()
result = g.parse("http://dbpedia.org/resource/Queens_of_the_Stone_Age")

print("graph has %s statements." % len(g))
# prints graph has 79 statements.

for stmt in g.subject_objects(rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
    print stmt[1]


# purgatory
#for row in g.query('prefix dbpedia-owl: <http://dbpedia.org/ontology/> select ?s where { dbpedia:abstract ?s }'):
#	print row.s 