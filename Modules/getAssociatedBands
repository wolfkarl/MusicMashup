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