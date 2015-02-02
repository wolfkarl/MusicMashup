import rdflib
import rdfextras
rdfextras.registerplugins() 

mygraph= rdflib.Graph()
<<<<<<< HEAD
print ("[*] Starting to parse")
=======
print ("[*] Starting to parse pagerank-turtle-file")
>>>>>>> master
mygraph.parse('data/pagerank.ttl', format='n3')
print ("[*] Finished parsing")

results = mygraph.query("""
	PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
	SELECT DISTINCT ?rank WHERE {
	<http://dbpedia.org/resource/DJ_Sun> dbpedia-owl:wikiPageRank ?rank

	}
""")

<<<<<<< HEAD
for row in results:
    print ("Rank is: %s" % row)
=======
floddy_the_float = 0
for row in results:
	print (type(row))
	print row[0]
    # print ("Rank is: %s" % row)
>>>>>>> master
