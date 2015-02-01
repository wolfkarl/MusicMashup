import rdflib
import rdfextras
rdfextras.registerplugins() 

mygraph= rdflib.Graph()
print ("[*] Starting to parse")
mygraph.parse('data/pagerank.ttl', format='n3')
print ("[*] Finished parsing")

results = mygraph.query("""
	PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
	SELECT DISTINCT ?rank WHERE {
	<http://dbpedia.org/resource/DJ_Sun> dbpedia-owl:wikiPageRank ?rank

	}
""")

for row in results:
    print ("Rank is: %s" % row)