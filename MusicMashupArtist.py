# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

import re
import string
import json

import urllib
from urllib import urlopen

from titlecase import titlecase

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist

class MusicMashupArtist:

	songkickApiKey = "BxSDhcU0tXLU4yHQ"

	# Instanzvariablen
	# erlaubt das halten von URLs etc. über einzelne Funktionen hinaus

	# dbpediaURL = None
	# dbtuneURL = None
	# musicbrainzID = 0
	# echoNestArtist = None
	# spotifyID = 0
	# songkickID = 0
	# state = 0
	# problem = ""
	# events = None
	# recommendation = []
	# reason = []

	# related = []
	# abstract = ""

	# currentMembers = []
	# formerMembers = []
	# relatedSources = []

	def __init__(self, query, reco = ""):
		self.dbpediaURL = None
		self.dbtuneURL = None
		self.musicbrainzID = 0
		self.echoNestArtist = None
		self.spotifyID = 0
		self.songkickID = 0
		self.state = 0
		self.problem = ""
		self.eventsJSON = None
		self.events = []
		self.recommendation = []
		self.reason = []

		self.related = []
		self.abstract = ""

		self.dbpedia_set = 0
		self.dbtune_set = 0

		self.currentMembers = []
		self.formerMembers = []
		self.formerMembersNR = []
		self.currentMembersNR = []
		self.relatedSources = []

		self.soloArtist = False

		self.dbpediaCommonsURL = None
		self.thumbnail = None
		self.images = []

		query = urllib.unquote(query)

		if query[:4] == "http":
			self.name = self._uri_to_name(query)
			self.dbpediaURL = query
			self.dbpedia_set = 1
			self.thumbnail = None
		else:
			self.name = titlecase(query)


		if reco != "":
			self.reason.append(reco)




		# locate artist on musicbrainz (via dbtune) and dbpedia
		print("[~][~] Fetching data sources for " + self.get_name())
		self._find_resources()
		if self.state == 0:
			print("[+] done")

	# ========================================================================================
	# 	GETTER 
	# (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)
	# ========================================================================================


	def _find_resources(self):
		self._pull_dbtune()
		
		# hier mit Fallback anfangen

		# print (not self.dbtuneURL)

		if not self.dbtuneURL:
			print ("[-] Could not find Resource on DBTune => Trying with musicbrainz dump now")
			self._pull_mbdump()
			print ("[~] Trying again for DBPedia")
			self._pull_dbpedia_url_from_dbpedia()
		else:
			if self.dbtuneURL and not self.dbpediaURL:
				self._pull_dbpedia_url()

		if self.dbpediaURL:
			self._pullThumbnail()
			self._decodeURL()

		if not self.dbpediaURL and not self.dbtuneURL:
			self.set_error_state()

	def get_dbpediaURL_link(self, url=""):
		if url:
			return urllib.quote_plus(url.encode('utf8'))
		else:
			return urllib.quote_plus(self.get_dbpediaURL().encode('utf8'))

	def	_decodeURL(self):
		self.dbpediaURL = string.replace(self.dbpediaURL, '%28', '(')
		self.dbpediaURL = string.replace(self.dbpediaURL, '%29', ')')

	def getThumbnail(self):
		return self.thumbnail

	def _pullThumbnail(self):
		try:
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

				SELECT ?o
				WHERE {
				<"""+self.get_dbpediaURL()+"""> dbpedia-owl:thumbnail ?o
				}""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			for result in results["results"]["bindings"]:
				self.thumbnail = result["o"]["value"]
				print ("[+] Found Thumbnail: "+ self.thumbnail)
		except:
			print ("[-] error while pulling thumbnail")

	def get_images(self):
		self._pull_commons()
		return self.images

	def get_current_members(self):
		return self.currentMembers

	def get_former_members(self):
		return self.formerMembers

	def get_current_membersNR(self):
		return self.currentMembersNR

	def get_former_membersNR(self):
		return self.formerMembersNR

	def _pull_commons(self):
		try:
			print("[~] Pulling Commomns ")
			sparql = SPARQLWrapper("http://commons.dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			    SELECT ?band
			    WHERE { 
			      ?band rdfs:label \""""+self.get_name()+"""\"@en .
			}""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			
			for result in results["results"]["bindings"]:
			    self.dbpediaCommonsURL = result["band"]["value"]

			if self.dbpediaCommonsURL:
				self.dbpediaCommonsURL = self.dbpediaCommonsURL.replace('Category:', '')
				print "==================="
				print ("[+] Found Commons "+self.dbpediaCommonsURL)
				print "==================="

				sparql.setQuery("""
				    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				    PREFIX mo: <http://purl.org/ontology/mo/>

				    SELECT ?url
				    WHERE { 
				      <"""+self.dbpediaCommonsURL+"""> dbpedia-owl:galleryItem ?picture .
				      ?picture dbpedia-owl:fileURL ?url
				    }
				""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()

				for result in results["results"]["bindings"]:
				    self.images.append(result["url"]["value"])
				    # print result["url"]["value"]
			else: 
				print ("[-] There was no commons entry for this band")
		except:
			print ("[-] error while pulling commons")

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

			lastSix = self.name[len(self.get_name())-6:]
			# print lastSix
			if not self.dbtuneURL and (lastSix == "(Band)" or lastSix == "(band)"):
				withoutBand = self.get_name()[:-6]
				if withoutBand[len(withoutBand)-1:] == " ":
					withoutBand = withoutBand[:-1]
					print("SOGAR EIN LEERZEICHEN WAR DA")


				print ("Trying with: "+self.get_name()[:-6])
				sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
				sparql.setQuery("""
					PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
					PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
					PREFIX mo: <http://purl.org/ontology/mo/>
					SELECT ?s
					WHERE { 
					?s rdfs:label \""""+withoutBand+"""\" .
					?s rdf:type mo:MusicArtist .
					}
				""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()
			for result in results["results"]["bindings"]:
				self.dbtuneURL = result["s"]["value"]

			#Oft hat musicbrainz ein The XY und dbtune kein The bzw vice versa, daher:
			nameshort = self.name[:3]
			if not self.dbtuneURL and (nameshort != "The"):
				print ("[~] Trying with 'The' XY")
				sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
				sparql.setQuery("""
					PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
					PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
					PREFIX mo: <http://purl.org/ontology/mo/>
					SELECT ?s
					WHERE { 
					?s rdfs:label \"The """+self.get_name()+"""\" .
					?s rdf:type mo:MusicArtist .
					}
				""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()
				for result in results["results"]["bindings"]:
					self.dbtuneURL = result["s"]["value"]
				if self.dbtuneURL:
					self.name = "The "+self.name

			if self.dbtuneURL:
				self.musicbrainzID = self.dbtuneURL[-36:]
				print("[+] Found dbtune URL")
				print("[+] musicbrainzID: "+self.musicbrainzID)
				self.dbtune_set = 1
				return 0
			else:
				self.dbtune_set = -1
				return -1
		except:
			self.problem = "dbtune problem while fetching dbtune url"
			print("[-] dbtune problem while fetching dbtune url")
			self.dbtune_set = -1
			return -1

	def _pull_mbdump(self):
		try:
			sparql = SPARQLWrapper("http://141.89.225.50:8896/sparql")
			sparql.setQuery("""
				PREFIX foaf: <http://xmlns.com/foaf/0.1/>

	    		SELECT ?artist
	    		WHERE { 
	    		?artist foaf:name \""""+self.get_name()+"""\".
	    		}
				""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			for result in results["results"]["bindings"]:
	   			self.musicbrainzID = result["artist"]["value"][30:-2]

	   		print (self.musicbrainzID)
	   	except:
			print ("[-] error while pulling")

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
		try:
			if not self.abstract and self.state == 0:
				print("[~] Pulling abstract for: "+self.get_dbpediaURL())
				self.abstract = self._pull_abstract()
		except:
			self.abstract = "Abstract Error"
		return self.abstract

	def get_abstract_excerpt(self, len=100):
		a =  self.get_abstract()
		return a[:len]+"..."

	def _pull_abstract(self):
		try:
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

				SELECT ?o
				WHERE { 
				<"""+self.get_dbpediaURL()+"""> dbpedia-owl:abstract ?o .
				FILTER(langMatches(lang(?o), "EN"))
				}
				""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			for result in results["results"]["bindings"]:
				self.abstract = result["o"]["value"]
			return self.abstract
		except:
			print ("[-] error while pulling abstract")
	# ========================================================================================
	# SPOTIFY get and _pull
	# ========================================================================================

	def get_spotify_id(self):
		if self.state == 0:
			if not self.spotifyID:
				print("[~] Pulling Spotify ID")
				self.spotifyID = self._pull_spotify_id()
				return self.spotifyID
		else:
			return "0000"

	def _pull_spotify_id(self):
		try:
			if self.dbtune_set == 1:
				self.spotifyID = self.get_echoNestArtist().get_foreign_id('spotify')
			else:
				self.spotifyID = "1234"
			return self.spotifyID
		except:
			self.spotifyID = "2345"
			return self.spotifyID


	# ========================================================================================
	# DBTUNE-URL get and _pull
	# ========================================================================================
	def get_dbtuneURL(self):
		if not self.dbtuneURL:
			self.dbtuneURL = self._pull_dbtune()
		return self.dbtuneURL

	def get_dbpediaURL(self):
		if not self.dbpediaURL:
			self.dbpediaURL = self._pull_dbpedia_url()
		return self.dbpediaURL

	def _pull_dbpedia_url(self):
		try:
			print("[~] Trying to pull dbpedia url")
			sparql = SPARQLWrapper("http://dbtune.org/musicbrainz/sparql")
			sparql.setQuery("""
					PREFIX owl: <http://www.w3.org/2002/07/owl#>

					SELECT ?o
					WHERE {
					<"""+self.get_dbtuneURL()+"""> owl:sameAs ?o .
					}
					""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			for result in results["results"]["bindings"]:
				if "dbpedia.org/resource" in result["o"]["value"]:
					self.dbpediaURL = result["o"]["value"]

			if self.dbpediaURL:
				print("[+] Found dbpedia URL")
				return 0
			else:
				#TODO wird nicht geprinted wenn keine dbpedia url
				print ("[-] Could not find dbpedia URL")
				return -1

		except:
			self.problem = "dbtune problem while fetching dbpedia url"
			print("[-] dbtune problem while fetching dbpedia url")
			return -1

	def _pull_dbpedia_url_from_dbpedia(self):
		try:
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				SELECT ?s
				WHERE {
				?s rdfs:label \""""+self.get_name()+"""\"@en.
				?s dbpedia-owl:background "group_or_band".
				}
				""")

			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()

			for result in results["results"]["bindings"]:
				if "dbpedia.org/resource" in result["s"]["value"]:
					self.dbpediaURL = result["s"]["value"]

					if self.dbpediaURL:
						print("[+] Found dbpedia URL")
						return 0
					else:
						#TODO wird nicht geprinted wenn keine dbpedia url
						print ("[-] Could not find dbpedia URL")
						return -1
		except:
			print ("[-] error while pulling dbpediaURL from dbpedia")

	# ========================================================================================
	# RELATED get and _pull
	# ========================================================================================
	def get_related(self):
		# if not self.related:
		print("[~] get_related")
		self.related = []
		self.currentMembers = []
		self.formerMembers = []
		self.relatedSources = []
		self._pull_related()
		# self.recommendation = sorted(self.recommendation, key=lambda reco: len(reco))
		# self.recommendation = sorted(self.recommendation, key=lambda reco: len(reco))

		return self.recommendation

	def get_reason(self):
		return self.reason

	def _pull_related(self):
		# get Methoden sollten noch geschrieben werden
		try:
			self._pull_current_members()
			self._pull_former_members()
			if not self.currentMembers and not self.formerMembers:
				print("[~] No members => Trying Resource as Solo-Artist")
				self.soloArtist = True
			self._pull_current_bands_of_current_members()
			self._pull_former_bands_of_current_members()
			self._pull_current_bands_of_former_members()
			self._pull_former_bands_of_former_members()
		except:
			pass # bestes error handling aller zeiten
		
		try:	
			self._pull_producer_relation()
		except:
			pass
		# self.parse_to_rdf()
		# self._pull_events()
		# return self.related

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

	# ========================================================================================
	# SONGKICK-EVENTS get and _pull
	# ========================================================================================

	def get_events(self):
		self._pull_events()
		return self.events

	def _pull_events(self):
		try:
			print ("[~] Pulling Songkick Events")
			self.eventsJSON = urlopen('http://api.songkick.com/api/3.0/artists/mbid:'+str(self.musicbrainzID)+'/calendar.json?apikey='+self.songkickApiKey+'').read()
			self.eventsJSON = json.loads(self.eventsJSON)
			self._convert_events()
		except:
			print ("[-] error while pulling events")

	def _convert_events(self):
		# entries = self.eventsJSON["resultsPage"]["totalEntries"]
		# print (entries)
		entries = 0
		# print (type(self.eventsJSON["resultsPage"]["totalEntries"]))
		if (self.eventsJSON["resultsPage"]["totalEntries"]) != 0:
			entries = len(self.eventsJSON["resultsPage"]["results"]["event"])
		# print (entries)
		if entries > 0:
			for i in range(entries):
				self.events.append(self.eventsJSON["resultsPage"]["results"]["event"][i]["displayName"])
		else:
			self.events.append("No Concerts found.")

	# ========================================================================================
	# MEMBER _pull
	# ========================================================================================

	def _pull_current_members(self):
		try:
			print("[~] Pulling current Members of: "+self.get_dbpediaURL())
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbprop: <http://dbpedia.org/property/>

				SELECT ?member WHERE {
	    			<"""+self.get_dbpediaURL()+"""> dbprop:currentMembers ?member.
					}
				""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()			

			for result in results["results"]["bindings"]:
				if result["member"]["value"][:4] == "http" and 'List_of' not in result["member"]["value"]:
					self.currentMembers.append(result["member"]["value"])
					print result["member"]["value"]
				else:
					self.currentMembersNR.append(result["member"]["value"])
					print("[-] No Resource on dbpedia for: "+result["member"]["value"])

			if not self.currentMembers:
				print("[~] Pulling current Members of: "+self.get_dbpediaURL()+" with dbpedia-owl:bandMembers")
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
					SELECT ?member WHERE {
		    			<"""+self.get_dbpediaURL()+"""> dbpedia-owl:bandMembers ?member.
						}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()			

				for result in results["results"]["bindings"]:
					if result["member"]["value"][:4] == "http" and 'List_of' not in result["member"]["value"]:
						self.currentMembers.append(result["member"]["value"])
						print result["member"]["value"]
					else:
						self.currentMembersNR.append(result["member"]["value"])
						print("[-] No Resource on dbpedia for: "+result["member"]["value"])
		except:
			print ("[-] error while pulling current members")

	def _pull_former_members(self):
		try:
			print("[~] Pulling former Members of: "+self.get_dbpediaURL())
			sparql = SPARQLWrapper("http://dbpedia.org/sparql")
			sparql.setQuery("""
				PREFIX dbprop: <http://dbpedia.org/property/>
				PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

				SELECT ?member WHERE {
	    			<"""+self.get_dbpediaURL()+"""> dbpedia-owl:formerBandMember ?member.
					}
				""")
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()			

			for result in results["results"]["bindings"]:
				if result["member"]["value"][:4] == "http" and 'List_of' not in result["member"]["value"]:
					self.formerMembers.append(result["member"]["value"])
					print result["member"]["value"]
				else:
					self.formerMembersNR.append(result["member"]["value"])
					print("[-] No Resource on dbpedia for: "+result["member"]["value"])

			if not self.formerMembers:
				print("[~] Pulling former Members of: "+self.get_dbpediaURL()+" with dbpprop:pastMembers")
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT ?member WHERE {
		    			<"""+self.get_dbpediaURL()+"""> dbpprop:pastMembers ?member.
						}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()			

				for result in results["results"]["bindings"]:
					if result["member"]["value"][:4] == "http" and 'List_of' not in result["member"]["value"]:
						self.formerMembers.append(result["member"]["value"])
						print result["member"]["value"]
					else:
						self.formerMembersNR.append(result["member"]["value"])
						print("[-] No Resource on dbpedia for: "+result["member"]["value"])
		except:
			print ("[-] error while pulling former members")

	# ===============================================================
	# TODO ERROR-HANDLING
	# 			ab hier untegesteter code ohne error handling
	# ===============================================================

	def _pull_producer_relation(self):
		try:
			for member in self.currentMembers:
				print ("[~] searching producer relations for: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
					SELECT DISTINCT ?band WHERE {
		    			?production dbprop:producer <"""+member+""">.
		    			?production dbpedia-owl:artist ?band.
						}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(member)+" was active as producer"))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was active as producer")

			if self.soloArtist:
				print ("[~] searching producer relations for maybe solo-Artist: "+ self.get_dbpediaURL())
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
					SELECT DISTINCT ?band WHERE {
		    			?production dbprop:producer <"""+self.get_dbpediaURL()+""">.
		    			?production dbpedia-owl:artist ?band.
						}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as producer"))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as producer")
		except:
			print ("[-] error while pulling producer relation")

	def _pull_current_bands_of_current_members(self):
		try:
			for member in self.currentMembers:
				print ("[~] searching current band of current member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:bandMember <"""+member+""">.
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(member)+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" is also a member of this band.")

			if self.soloArtist:
				print ("[~] searching current band of maybe solo-artist: "+ self.get_dbpediaURL())
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:bandMember <"""+self.get_dbpediaURL()+""">.
		    			}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band.")
		except:
			print ("[-] error while pulling")

	def _pull_former_bands_of_current_members(self):
		try:
			for member in self.currentMembers:
				print ("[~] searching former band of current member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:formerBandMember <"""+member+""">.
		    			}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]: 
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(member)+" was also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was also a member of this band.")

			if self.soloArtist:
				print ("[~] searching former band of maybe solo-artist: "+ self.get_dbpediaURL())
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:formerBandMember <"""+self.get_dbpediaURL()+""">.
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band.")
		except:
			print ("[-] error while pulling former bands of current members")

	def _pull_current_bands_of_former_members(self):
		try:
			if self.soloArtist:
				return 0
			print ("[~] Searching current Bands of former Members")
			for member in self.formerMembers:
				print ("[~] searching current bands of former member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:bandMember <"""+member+""">.
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]: 
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.get_dbpediaURL():
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(member)+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" is also a member of this band.")
		except:
			print ("[-] error while pulling current bands of former Members")

	def _pull_former_bands_of_former_members(self):
		try:
			if self.soloArtist:
				return 0
			print ("[~] Searching current Bands of former Members")
			for member in self.formerMembers:
				print ("[~] searching former bands of former member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?band WHERE {
		    			?band dbpedia-owl:formerBandMember <"""+member+""">.
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["band"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["band"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["band"]["value"] == r.dbpediaURL:
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], "Because "+self._uri_to_name(member)+" was also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was also a member of this band.")
		except:
			print ("[-] error while pulling former bands of former members")	

	def _uri_to_name(self, uri):
		# print("[~] Converting URI to name")
		uri = uri[28:]
		uri = uri.replace('_', ' ')
		return uri

	def uri_to_name_if_necessary(self, uri):
		if uri[:4] == "http":
			return self._uri_to_name(uri)
		else:
			return uri

	def addReason(self, reason):
		self.reason.append(reason)

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
		file.write("<"+self.get_dbpediaURL()+"> dbpedia-owl:abstract \""+self.abstract+"\" .\n")
	
	def parse_current_members(self, file):
		for member in self.currentMembers:
			file.write("<"+self.get_dbpediaURL()+"> dbprop:currentMember <"+member+"> .\n")
	def parse_related_artists(self, file):
		for artist in self.relatedSources:
			file.write("<"+self.get_dbpediaURL()+"> dbpedia-owl:associatedMusicalArtist <"+artist+"> .\n")

	# ========================================================================================
	# brauchen wir das noch?
	# ========================================================================================

	# def _pull_songkick_id(self):
	# 	self.songkickID = self.get_echoNestArtist().get_foreign_id('songkick')
	# 	return self.songkickID

# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Queens of the Stone Age")
	print("this is a test.")
	print(test.get_name())
	print(test.get_abstract())
	print(test.get_spotify_id())
	# print(test.get_abstract())
	# print(test.dbtuneURL)
	# print (test.dbpediaURL)
	blubb = test.get_related()
	# print(blubb)
	for r in blubb:
		print(" + "+r.get_name() + " - " + r.get_abstract_excerpt(50) + " - " + r.get_spotify_id())
