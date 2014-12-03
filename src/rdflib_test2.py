from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    SELECT ?abstract
    WHERE { 
      <http://dbpedia.org/resource/Queens_of_the_Stone_Age> dbpedia-owl:abstract ?abstract .
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print result["abstract"]["value"]