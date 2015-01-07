from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://commons.dbpedia.org/sparql")
sparql.setQuery("""
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX mo: <http://purl.org/ontology/mo/>

    SELECT ?band
    WHERE { 
      ?band rdfs:label "Led Zeppelin"@en .
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

dbpediaCommonsURL = 0

for result in results["results"]["bindings"]:
    dbpediaCommonsURL = result["band"]["value"]

print "==================="
print dbpediaCommonsURL
print "==================="
# Category muss raus...

dbpediaCommonsURL = dbpediaCommonsURL.replace('Category:', '')

print dbpediaCommonsURL
print "==================="

sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX mo: <http://purl.org/ontology/mo/>

    SELECT ?url
    WHERE { 
      <"""+dbpediaCommonsURL+"""> dbpedia-owl:galleryItem ?picture .
      ?picture dbpedia-owl:fileURL ?url
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

pictureList = []

for result in results["results"]["bindings"]:
    pictureList.append(result["url"]["value"])

for item in pictureList:
    print item

print "==================="


# pictureURLs = []

# for item in pictureList:
#     sparql.setQuery("""
#         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#         PREFIX mo: <http://purl.org/ontology/mo/>

#         SELECT ?url
#         WHERE { 
#           <"""+item+"""> dbpedia-owl:fileURL ?url .
#         }
#     """)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()



