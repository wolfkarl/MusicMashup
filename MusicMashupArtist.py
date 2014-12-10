# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist

class MusicMashupArtist:

	# Globale Variablen
	# erlaubt das halten von URLs etc. über einzelne Funktionen hinaus

	dbpediaURL = None
	dbtuneURL = None
	musicbrainzID = None
	echoNestArtist = None
	spotifyID = None
	songkickID = None
	currentMembers = []
	formerMembers = []

	def __init__(self, query, reco = ""):
		self.name = query
		self._find_resources()
		self.abstract = ""
		self.musicbrainzID = self._pull_musicbrainz_id(self.dbtuneURL)
		self.echoNestArtist = self._pull_echonext_artist(self.musicbrainzID)
		self.spotifyID = self._pull_spotify_id(self.echoNestArtist)
		self.songkickID = self._pull_songkick_id(self.echoNestArtist)
		self.related = []
		self.reco = reco
		self._pull_current_members()


	# Getter (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)

	def get_name(self):
		return self.name

	def get_abstract(self):
		if not self.abstract:
			print("[~] Pulling abstract")
			self.abstract = self._pull_abstract()
		return self.abstract

	def get_abstract_excerpt(self, len=100):
		a =  self.get_abstract()
		return a[:len]+"..."

	def get_upcoming_tours(self):
		pass

	def get_spotify_uri(self):
		#hardcode
		# return "spotify:track:4th1RQAelzqgY7wL53UGQt" #avicii
		# if not self.spotifyID
		# 	print("[~] Pulling Spotify ID")
		# 	self.spotifyID = self.
		return self.spotifyID

	def get_related(self):
		if not self.related:
			self.related = self._pull_related()
		return self.related

	def get_reco(self):
		return self.reco


	# find_resources sucht bei DBTunes nach der entsprechenden Ressource und speichert diese (siehe globvars)

	def _find_resources(self):
		# global dbpediaURL, dbtuneURL

		sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
		sparql.setQuery("""
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX mo: <http://purl.org/ontology/mo/>

			SELECT ?s
			WHERE { 
			?s rdfs:label \""""+self.get_name()+"""\" .
			?s rdf:type mo:MusicArtist .
			}
			""")

		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			self.dbtuneURL = result["s"]["value"]

		sparql.setQuery("""
			PREFIX owl: <http://www.w3.org/2002/07/owl#>

			SELECT ?o
			WHERE {
			<"""+self.dbtuneURL+"""> owl:sameAs ?o .
			}
			""")

		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			if "dbpedia.org/resource" in result["o"]["value"]:
				self.dbpediaURL = result["o"]["value"]
		# print self.dbpediaURL
		# return self.dbpediaURL

	def _pull_abstract(self):
		# global dbpediaURL, dbtuneURL

		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery("""
			PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

			SELECT ?o
			WHERE { 
			<"""+self.dbpediaURL+"""> dbpedia-owl:abstract ?o .
			FILTER(langMatches(lang(?o), "EN"))
			}
			""")


		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			abstract = result["o"]["value"]

		return abstract

	def _pull_related(self):
		#hardcode
		# self.related.append(MusicMashupArtist("Helene Fischer", "Because both are on Universal Label"))
		# self.related.append(MusicMashupArtist("Deep Twelve", "Because both bands have <a href='#'>Marvin Gay</a> play Bass"))
		# self.related.append(MusicMashupArtist("John Scofield", "Because both were produced by Josh Homme"))
		return self.related

	# holt aus der aktuellen dbtune-Resource-URI die Musicbrainz ID
	def _pull_musicbrainz_id(self, dbtune):
		musicbrainzID = dbtune[-36:]
		return musicbrainzID

	# holt den echoNest-Artist anhand der MusicbrainzID
	def _pull_echonext_artist(self, mbid):
		echoNestArtist = artist.Artist('musicbrainz:artist:'+mbid)
		return echoNestArtist

	#holt die spotifyID anhand des echoNest Artists
	def _pull_spotify_id(self, echonestArtist):
		spotifyID = echonestArtist.get_foreign_id('spotify')
		return spotifyID

	def _pull_songkick_id(self, echonestArtist):
		songkickID = echonestArtist.get_foreign_id('songkick')
		return songkickID

	def _pull_current_members(self):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery("""
			PREFIX dbprop: <http://dbpedia.org/property/>

			SELECT ?member WHERE {
    			<"""+self.dbpediaURL+"""> dbprop:currentMembers ?member.
				}
			""")
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()			

		for result in results["results"]["bindings"]:
			self.currentMembers.append(result["member"]["value"])

	# def _pull_producer_relation (self):
	# 	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	# 	sparql.setQuery("""
	# 		PREFIX dbprop: <http://dbpedia.org/property/>
	# 		SELECT ?member WHERE {
 #    			<"""+self.dbpediaURL+"""> dbprop:currentMembers ?member.
	# 			}
	# 		""")


# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Queens of the Stone Age")
	print(test.get_name())
	print(test.get_abstract())
	print(test.get_abstract())
	blubb = test.get_related()
	print(blubb)
	for r in blubb:
		print(" + "+r.get_name())
