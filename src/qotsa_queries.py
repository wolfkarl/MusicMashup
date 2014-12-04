from SPARQLWrapper import SPARQLWrapper, JSON

input = "Queens of the Stone Age"

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

url = None

for result in results["results"]["bindings"]:
    url = result["s"]["value"]

# print url

sparql.setQuery("""
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX mo: <http://purl.org/ontology/mo/>

    SELECT ?p ?o
    WHERE { 
    	<"""+url+"""> ?p ?o .
    }
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# for result in results["results"]["bindings"]:
# 	print result["p"]["value"] +" - "+ result["o"]["value"]

dbpediaUrl = None
musicbrainzID = None

for result in results["results"]["bindings"]:
	if "dbpedia.org/resource" in result["o"]["value"]:
		dbpediaUrl = result["o"]["value"]
	if "musicbrainz.org" in result["o"]["value"]:
		musicbrainzID = result["o"]["value"]


print dbpediaUrl
print musicbrainzID

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX mo: <http://purl.org/ontology/mo/>

    SELECT ?p ?o
    WHERE { 
    	<"""+dbpediaUrl+"""> ?p ?o .
    }
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
	print result["p"]["value"] +" - "+ result["o"]["value"]