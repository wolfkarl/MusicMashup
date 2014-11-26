import rdflib
from rdflib import Graph
from rdflib import URIRef, Literal, BNode, Namespace, ConjunctiveGraph
from rdflib import RDF
from rdflib import RDFS
from SPARQLWrapper import SPARQLWrapper, JSON


inputArtists = []
inputArtists.append("Queens Of The Stone Age")
inputArtists.append("Okta Logue")
inputArtists.append("Antilopen Gang")

inputArtistsRelatet = Graph()

def getAssociatedBands(url):
	sparql = SPARQLWrapper("http://www.dbpedia.org/sparql")
	sparql.setQuery("""
	    SELECT ?associatedBand
	    WHERE { 
	      <"""+url+"""> dbpedia-owl:associatedBand ?associatedBand .
	    }
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
	    print result["associatedBand"]["value"]



# for artist in inputArtists:
# 	print artist

# numberOfInputArtists=len(inputArtists)
# for i in range(0,numberOfInputArtists):
#     inputArtistsRelatet.append()



#FUNZT 
# g = Graph()
# g.parse("http://dbpedia.org/resource/Queens_of_the_Stone_Age")

# print("graph has %s statements." % len(g))

# for stmt in g.subject_objects(URIRef("http://dbpedia.org/ontology/associatedBand")):
#      print stmt
qotsa = "http://dbpedia.org/resource/Queens_of_the_Stone_Age"
getAssociatedBands(qotsa)

