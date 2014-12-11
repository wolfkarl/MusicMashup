# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

import re

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist

class MusicMashupArtist:

	# Globale Variablen
	# erlaubt das halten von URLs etc. über einzelne Funktionen hinaus

	dbpediaURL = None
	dbtuneURL = None
	musicbrainzID = 0
	echoNestArtist = None
	spotifyID = 0
	songkickID = 0
	state = 0
	problem = ""

	related = []
	abstract = ""

	currentMembers = []
	formerMembers = []
	relatedSources = []

	def __init__(self, query, reco = ""):
		self.name = query
		# self._find_resources()

		self.dbpediaURL = "http://dbpedia.org/resource/Queens_of_the_Stone_Age"
		# Hardcode Musicbrainz ID
		self.musicbrainzID = "7dc8f5bd-9d0b-4087-9f73-dc164950bbd8"
		# self.state = 0

		# reco = recommendation reason
		self.reco = reco

		# locate artist on musicbrainz (via dbtune) and dbpedia
		print("[~] Fetching data sources for " + self.get_name())
		# self._find_resources()
		if self.state == 0:
			print("[+] done")

		


	# ========================================================================================
	# 	GETTER 
	# (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)
	# ========================================================================================

	def get_name(self):
		return self.name

	def get_abstract(self):
		if not self.abstract and self.state == 0:
			print("[~] Pulling abstract")
			self.abstract = self._pull_abstract()
		return self.abstract

	def get_abstract_excerpt(self, len=100):
		a =  self.get_abstract()
		return a[:len]+"..."

	def get_upcoming_tours(self):
		pass

	def get_spotify_uri(self):
		if self.state == 0:
			if not self.spotifyID:
				print("[~] Pulling Spotify ID")
				self.spotifyID = self._pull_spotify_id()
			return self.spotifyID
		else:
			return "0000"


	def get_dbtuneURL(self):
		if not self.dbtuneURL:
			self.dbtuneURL = _pull_dbtune()
		return self.dbtuneURL

	def get_related(self):
		if not self.related:
			self.related = self._pull_related()
		return self.related

	def get_reco(self):
		return self.reco

	def get_echonestArtist(self):
		if not self.echoNestArtist and self.state == 0:
			self._pull_echonest_artist()
		else:
			return -1


	def set_error_state(self):
		print("[-] Could not locate Open Data source. Switching to error state!")
		self.abstract = "Abstract not available. (" + self.problem + ")"
		self.state = -1

	# ========================================================================================
	# 	PULLER 
	# ========================================================================================

	def _find_resources(self):
		self._pull_dbtune()
		if self.dbtuneURL:
			self._pull_dbpedia_url()

		if not self.dbpediaURL or not self.dbtuneURL:
			self.set_error_state()


	def _pull_dbtune(self):
		try:
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

			if self.dbtuneURL:
				self.musicbrainzID = self.dbtuneURL[-36:]
				#Hardcode
				self.musicbrainzID = "7dc8f5bd-9d0b-4087-9f73-dc164950bbd8"
				print("[+] Found dbtune URL")
				return 0
			else:
				return -1
		except:
			self.problem = "dbtune problem"
			print("[-] dbtune problem")
			return -1


	def _pull_dbpedia_url(self):
		try:
			sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
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

			if self.dbpediaURL != "":
				print("[+] Found dbpedia URL")

				return 0
			else:
				return -1

		except:
			self.problem = "dbtune problem while fetching dbpedia url"
			print("[-] dbtune problem")
			return -1



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

		abstract = None

		for result in results["results"]["bindings"]:
			abstract = result["o"]["value"]

		return abstract

	def _pull_related(self):
		#hardcode
		# self.related.append(MusicMashupArtist("Helene Fischer", "Because both are on Universal Label"))
		# self.related.append(MusicMashupArtist("Deep Twelve", "Because both bands have <a href='#'>Marvin Gay</a> play Bass"))
		# self.related.append(MusicMashupArtist("John djfakdjfkajfdkjfd", "To test non-existing artists"))
		self._pull_current_members()
		self._pull_producer_relation()
		self._pull_current_bands_of_current_members()
		return self.related


	# holt den echoNest-Artist anhand der MusicbrainzID
	def _pull_echonest_artist(self):
		if self.musicbrainzID:
			self.echoNestArtist = artist.Artist('musicbrainz:artist:'+self.musicbrainzID)
			# self.echonestArtist = echoNestArtist
			print ("[+] Found echoNestArtist")
			# return echoNestArtist
		else:
			return -1

	#holt die spotifyID anhand des echoNest Artists
	def _pull_spotify_id(self):
		self.get_echonestArtist()
		self.spotifyID = self.echoNestArtist.get_foreign_id('spotify')
		return self.spotifyID

	def _pull_songkick_id(self):
		self.get_echonestArtist()
		self.songkickID = self.echoNestArtist.get_foreign_id('songkick')
		# return songkickID


 # 			ab hier untegesteter code ohne error handling
 # ========================== vvvvvvvvvvvvv ===============================


	def _uri_to_name (self, uri):
		uri = uri[28:]
		uri = uri.replace('_', ' ')
		return uri

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
			print result["member"]["value"]

	def _pull_producer_relation (self):
		for member in self.currentMembers:
			print ("[~] searching producer relations for: "+ member)
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbprop: <http://dbpedia.org/property/>
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
				SELECT ?band WHERE {
	    			?production dbprop:producer <"""+member+""">.
	    			?production dbpedia-owl:artist ?band.
					}
				""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()	
			for result in results["results"]["bindings"]:
				if result["band"]["value"] != self.dbpediaURL and (result["band"]["value"] not in self.relatedSources) : 
					self.relatedSources.append(result["band"]["value"])
					self.related.append(MusicMashupArtist(self._uri_to_name(result["band"]["value"]), "Because "+self._uri_to_name(member)+" was active as producer"))
					print (result["band"]["value"])

	def _pull_current_bands_of_current_members (self):
		for member in self.currentMembers:
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

				SELECT ?band WHERE {
	    			?band dbpedia-owl:bandMember <"""+member+""">.
	    			}
				""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()	
			for result in results["results"]["bindings"]:
				if result["band"]["value"] != self.dbpediaURL and (result["band"]["value"] not in self.relatedSources) : 
					self.relatedSources.append(result["band"]["value"])
					self.related.append(MusicMashupArtist(self._uri_to_name(result["band"]["value"]), "Because "+self._uri_to_name(member)+" is also a member of this band."))
					print (result["band"]["value"])

	def _pull_former_bands_of_current_members (self):
		for member in self.currentMembers:
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

				SELECT ?band WHERE {
	    			?band dbpedia-owl:formerBandMember <"""+member+""">.
	    			}
				""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()	
			for result in results["results"]["bindings"]:
				if result["band"]["value"] != self.dbpediaURL and (result["band"]["value"] not in self.relatedSources) : 
					self.relatedSources.append(result["band"]["value"])
					self.related.append(MusicMashupArtist(self._uri_to_name(result["band"]["value"]), "Because "+self._uri_to_name(member)+" is also a member of this band."))
					print (result["band"]["value"])

# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Queens of the Stone Age")
	print(test.get_name())
	print(test.get_abstract())
	print(test.get_spotify_uri())
	# print(test.get_abstract())
	# print(test.dbtuneURL)
	# print (test.dbpediaURL)
	blubb = test.get_related()
	# print(blubb)
	for r in blubb:
		print(" + "+r.get_name() + " - " + r.get_abstract_excerpt(50) + " - " + r.get_spotify_uri())
