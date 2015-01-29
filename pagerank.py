import rdflib
import rdfextras
rdfextras.registerplugins() 

mygraph= rdflib.Graph()
mygraph.parse('data/pagerank_scores_en_2014.ttl', format='n3')

results = mygraph.query("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
					SELECT DISTINCT ?rank WHERE {
					<http://dbpedia.org/resource/Kyuss> dbpedia-owl:wikiPageRank ?rank

					}
					""")
for row in resluts:
    print row