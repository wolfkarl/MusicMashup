import rdflib
from rdflib import Graph
from rdflib import URIRef, Literal, BNode, Namespace, ConjunctiveGraph
from rdflib import RDF
from rdflib import RDFS
from SPARQLWrapper import SPARQLWrapper, JSON

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist


inputArtists = []
inputArtists.append("Queens Of The Stone Age")
inputArtists.append("Okta Logue")
inputArtists.append("Antilopen Gang")

inputArtistsRelatet = Graph()





# def getResource(userInput):
# 	sparql = SPARQLWrapper("http://www.dbpedia.org/sparql")
# 	sparql.setQuery("""
# 		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# 		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# 	    SELECT ?band
# 	    WHERE { 
# 	      ?band rdfs:label """+userInput+""".
# 	    }"""
# 	)
# 	sparql.setReturnFormat(JSON)
# 	results = sparql.query().convert()
# 	print "Resource for Input: " + userInput
# 	for result in results["results"]["bindings"]:
# 		print result["associatedBand"]["value"]
# 		return results


# def getAssociatedBands(url):
# 	sparql = SPARQLWrapper("http://www.dbpedia.org/sparql")
# 	sparql.setQuery("""
# 	    SELECT ?associatedBand
# 	    WHERE { 
# 	      <"""+url+"""> dbpedia-owl:associatedBand ?associatedBand .
# 	    }
# 	""")
# 	sparql.setReturnFormat(JSON)
# 	results = sparql.query().convert()
# 	print "Associated Bands for: " + url
# 	for result in results["results"]["bindings"]:
# 	    print result["associatedBand"]["value"]
# 	return results



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
# input = "\"Queens of the Stone Age\""
# qotsa = "http://dbpedia.org/resource/Queens_of_the_Stone_Age"
# gotsaRelatedArtits = getAssociatedBands(qotsa)
# getResource(input)




# def getArtist(mbID):
# artist = http://developer.echonest.com/api/v4/artist/search?api_key=GZVL1ZHROGIYXJZXG&name=radiohead
# print artist

dbpediaURL = None
dbtuneURL = None

def find_resources(input):
	global dbpediaURL, dbtuneURL
	sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
	sparql.setQuery("""
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX mo: <http://purl.org/ontology/mo/>
		SELECT ?s
		WHERE {
		?s rdfs:label \""""+input+"""\" .
		?s rdf:type mo:MusicArtist .
		}
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		dbtuneURL = result["s"]["value"]
	sparql.setQuery("""
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		SELECT ?o
		WHERE {
		<"""+dbtuneURL+"""> owl:sameAs ?o .
		}
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	for result in results["results"]["bindings"]:
		if "dbpedia.org/resource" in result["o"]["value"]:
			dbpediaURL = result["o"]["value"]
	return dbpediaURL

def get_musicbrainz_id(dbtune):
	mbid = dbtune[-36:]
	return mbid

qotsa = "Pink Floyd"
b = find_resources(qotsa)
print b


mbid = get_musicbrainz_id(dbtuneURL)
print mbid
echonestArtist = artist.Artist('musicbrainz:artist:'+mbid)
print echonestArtist.name
spotifyID = echonestArtist.get_foreign_id('spotify')
print spotifyID
songkickID = echonestArtist.get_foreign_id('songkick')
print songkickID


