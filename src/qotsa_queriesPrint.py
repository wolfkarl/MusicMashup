import json
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
sparql.setQuery("""
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX mo: <http://purl.org/ontology/mo/>

    SELECT ?s
    WHERE { 
      ?s rdfs:label "Queens of the Stone Age" .
      ?s rdf:type mo:MusicArtist .
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

url = 0

for result in results["results"]["bindings"]:
    url = result["s"]["value"]

print url

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
print results

with open('results.json', 'w') as outfile:
  json.dump(results, outfile)
# for result in results["results"]["bindings"]:
# 	print result["p"]["value"] +" - "+ result["o"]["value"]