# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

class MusicMashupArtist:

	# Globale Variablen
	# erlaubt das halten von URLs etc. über einzelne Funktionen hinaus

	dbpediaURL = None
	dbtuneURL = None
	related = []


	def __init__(self, query):
		self.name = query
		self._find_resources(query)
		self.abstract = ""


	# Getter (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)

	def get_name(self):
		return self.name

	def get_abstract(self):
		if not self.abstract:
			print("[~] Pulling abstract")
			self.abstract = self._pull_abstract()
		return self.abstract

	def get_upcoming_tours(self):
		pass

	def get_spotify_uri(self):
		#hardcode
		return "spotify:track:4th1RQAelzqgY7wL53UGQt" #avicii

	def get_related(self):
		if self.related.empty:
			self.related = self._pull_related
		return self.related


	# find_resources sucht bei DBTunes nach der entsprechenden Ressource und speichert diese (siehe globvars)

	def _find_resources(self, input):

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

	def _pull_abstract(self):
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

		for result in results["results"]["bindings"]:
			abstract = result["o"]["value"]

		return abstract

	def _pull_related(self):
		#hardcore
		self.related.append(MusicMashupArtist("Helene Fischer"))
		self.related.append(MusicMashupArtist("Deep Twelve"))
		self.related.append(MusicMashupArtist("John Scofield"))


# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Queens of the Stone Age")
	print(test.get_name())
	print(test.get_abstract())
	print(test.get_abstract())
