from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql/")
sparql.setQuery("""
    SELECT ?s
	WHERE {
  	?s rdfs:label "Queens of the Stone Age" .
  	?s rdf:type mo:MusicArtist
  	}
	""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# for result in results["results"]["bindings"]:
#     print result["abstract"]["value"]

print results