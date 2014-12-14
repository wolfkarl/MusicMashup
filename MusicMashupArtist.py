# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

import re

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist

class MusicMashupArtist:

	# Instanzvariablen
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

		# reco = recommendation reason
		# please rename
		self.reco = reco

		# locate artist on musicbrainz (via dbtune) and dbpedia
		print("[~] Fetching data sources for " + self.get_name())
		self._find_resources()
		if self.state == 0:
			print("[+] done")

	# ========================================================================================
	# 	GETTER 
	# (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)
	# ========================================================================================

	def get_name(self):
		return self.name


	def get_reco(self):
		return self.reco

	def set_error_state(self):
		print("[-] Could not locate Open Data source. Switching to error state!")
		self.abstract = "Abstract not available. (" + self.problem + ")"
		self.state = -1


	# ========================================================================================
	# ABSTRACT get and _pull
	# ========================================================================================
	def get_abstract(self):
		if not self.abstract and self.state == 0:
			print("[~] Pulling abstract")
			self.abstract = self._pull_abstract()
		return self.abstract

	def get_abstract_excerpt(self, len=100):
		a =  self.get_abstract()
		return a[:len]+"..."

	def _pull_abstract(self):
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
			self.abstract = result["o"]["value"]
		return self.abstract


	# ========================================================================================
	# TODO
	# UPCOMING EVENTS
	# ========================================================================================
	def get_upcoming_tours(self):
		pass


	# ========================================================================================
	# SPOTIFY get and _pull
	# ========================================================================================
	def get_spotify_uri(self):
		if self.state == 0:
			if not self.spotifyID:
				print("[~] Pulling Spotify ID")
				self.spotifyID = self._pull_spotify_id()
				return self.spotifyID
		else:
			return "0000"

	def _pull_spotify_id(self):
		self.spotifyID = self.get_echoNestArtist().get_foreign_id('spotify')
		return self.spotifyID


	# ========================================================================================
	# DBTUNE-URL get and _pull
	# ========================================================================================
	def get_dbtuneURL(self):
		if not self.dbtuneURL:
			self.dbtuneURL = _pull_dbtune()
		return self.dbtuneURL

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
			print("[-] dbtune problem while fetching dbpedia url")
			return -1



	# ========================================================================================
	# RELATET get and _pull
	# ========================================================================================
	def get_related(self):
		if not self.related:
			self.related = self._pull_related()
		return self.related

	def _pull_related(self):
		# get Methoden sollten noch geschrieben werden
		self._pull_current_members()
		self._pull_producer_relation()
		self._pull_current_bands_of_current_members()
		self._pull_former_bands_of_current_members()
		self.parse_to_rdf()
		return self.related


	# ========================================================================================
	# ECHONEST-ARTIST get and _pull
	# ========================================================================================
	def get_echoNestArtist(self):
		if not self.echoNestArtist and self.state == 0:
			print("[~] pulling echoNestArtist")
			self._pull_echoNest_artist()
			return self.echoNestArtist
		else:
			return self.echoNestArtist

	def _pull_echoNest_artist(self):
		if self.musicbrainzID:
			self.echoNestArtist = artist.Artist('musicbrainz:artist:'+self.musicbrainzID)
			print("[+] pulled echoNestArtist")
			return self.echoNestArtist
		else:
			return -1


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
				print("[+] Found dbtune URL")
				print(self.musicbrainzID)
				return 0
			else:
				return -1
		except:
			self.problem = "dbtune problem while fetching dbtune url"
			print("[-] dbtune problem while fetching dbtune url")
			return -1




	def _pull_songkick_id(self):
		self.songkickID = self.get_echoNestArtist().get_foreign_id('songkick')
		return self.songkickID




	# TODO ERROR-HANDLING
	# 			ab hier untegesteter code von paul ohne error handling
	# ===============================================================
	def _uri_to_name (self, uri):
		uri = uri[28:]
		uri = uri.replace('_', ' ')
		return uri



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


	# ========================================================================================
	# Parse Methoden
	# ========================================================================================

	def parse_to_rdf(self):
		filename = self.get_name().lower().replace(' ', '_')
		filepath = "dumps/"+filename
		# fileExists = os.path.exists(filepath)
		
		file = open(filepath, 'w+')
		
		self.parse_prefixes(file)
		self.parse_abstract(file)
		self.parse_current_members(file)
		
		self.parse_related_artists(file)
		file.close()
	
	def parse_prefixes(self, file):
		file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
		file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
		file.write("@prefix mo: <http://purl.org/ontology/mo/> .\n")
		file.write("@prefix dbpedia-owl: <http://dbpedia.org/ontology/> .\n")
		file.write("@prefix dbprop: <http://dbpedia.org/property/> .\n")
		file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
	
	def parse_abstract(self, file):
		file.write("<"+self.dbpediaURL+"> dbpedia-owl:abstract \""+self.abstract+"\" .\n")
	
	def parse_current_members(self, file):
		for member in self.currentMembers:
			file.write("<"+self.dbpediaURL+"> dbprop:currentMember <"+member+"> .\n")
	def parse_related_artists(self, file):
		for artist in self.relatedSources:
			file.write("<"+self.dbpediaURL+"> dbpedia-owl:associatedMusicalArtist <"+artist+"> .\n")



# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Queens of the Stone Age")
	print("this is a test.")
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
