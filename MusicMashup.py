# -*- coding: utf-8 -*-
### Irgendein Zeichen hat hier einen "not-ASCII-Eror" versucht, aber keine Ahnung welcher
""" Hauptklasse, wird erzeugt fuer jede Suchanfrage und stellt dann die Informationen ueber verschiedene Subklassen bereit """
from SPARQLWrapper import SPARQLWrapper, JSON

class MusicMashup:

# Imports



# Globale Variablen
# erlaubt das halten von URLs etc. über einzelne Funktionen hinaus

	dbpediaURL = None
	dbtuneURL = None

	def __init__(self, query):
		self.query = query
		self.find_resources(query)

	def description(self):
		return self.query + " "

	def upcoming_tours(self):
		pass

# find_resources sucht bei DBTunes nach der entsprechenden Ressource und speichert diese (siehe globvars)

	def find_resources(self, input):

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

	def get_abstract(self):

		global dbpediaURL, dbtuneURL

		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery("""
			PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

			SELECT ?o
			WHERE { 
			<"""+dbpediaURL+"""> dbpedia-owl:abstract ?o .
			FILTER(langMatches(lang(?o), "EN"))
			}
			""")

		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		abstract = None

		for result in results["results"]["bindings"]:
			abstract = result["o"]["value"]

		return abstract

		



