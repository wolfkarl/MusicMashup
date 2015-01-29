# -*- coding: utf-8 -*-
""" Repraesentiert einen Artist und alle dazugehoerigen Informationen. 

	Attribute werden immer ueber einen Getter angesprochen, beim ersten Aufruf wird ueber RDF gefetched. """
from SPARQLWrapper import SPARQLWrapper, JSON

import re
import string
import json
import discogs_client

import urllib
from urllib import urlopen

# for statistics
import time

from titlecase import titlecase

from pyechonest import config
config.ECHO_NEST_API_KEY="GZVL1ZHR0GIYXJZXG"
from pyechonest import artist
from MusicMashupParser import MusicMashupParser


cMcurrentBandVote = 3
fMcurrentBandVote = 1.5
cMformerBandVote  = 2
fMformertBandVote = 1
cMproducer = 1.5
fMproducer = 0.75
cMwriter = 0.8
fMwriter = 0.4

class MusicMashupArtist:
	# d = discogs_client.Client('ExampleApplication/0.1')
	parser = MusicMashupParser()
	songkickApiKey = "BxSDhcU0tXLU4yHQ"

	def __init__(self, query, voteValue = 0, reco = ""):
		self.starttime = time.clock()

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
		self.eventLinks = []
		self.recommendation = []
		self.reason = []

		self.related = []
		self.abstract = ""

		self.dbpedia_set = 0
		self.dbtune_set = 0

		self.further_urls = None
		self.discogs = None
		self.discogs_url = ""
		self.discogsArtist = None
		self.discogsID = None
		self.musixmatch = None
		self.musixmatch_url = ""
		self.official = ""
		self.lastfm = ""
		self.wikipedia = ""
		self.myspace = ""
		self.twitter = ""
		self.twitterUsername = ""

		self.currentMembers = []
		self.formerMembers = []
		self.formerMembersNR = []
		self.currentMembersNR = []
		self.relatedSources = []

		self.soloArtist = False

		self.dbpediaCommonsURL = None
		self.thumbnail = None
		self.images = []

		self.input = ""
		self.manualQuery = False
		if voteValue != 0:
			self.vote = voteValue
		else:
			self.vote = 0

		print "[+] Vote increased in constructor by: ",voteValue

		query = urllib.unquote(query)


		if query[:4] == "http":
			self.name = self._uri_to_name(query)
			self.input = self.name
			self.dbpediaURL = query
			self.dbpedia_set = 1
			self.thumbnail = None
		else:
			self.input = query
			self.name = titlecase(query)
			print ("[~] Converted to titlecase: "+ self.name)
			self.manualQuery = True


		if reco != "":
			self.reason.append(reco)
			




		# locate artist on musicbrainz (via dbtune) and dbpedia
		print("[~][~] Fetching data sources for " + self.get_name())
		self._find_resources()


	# ========================================================================================
	# 	GETTER 
	# (rufen puller auf falls noch nicht geschehen; spart Resourcen wenn nicht alles gebraucht wird)
	# ========================================================================================

	def start_parser(self):
		self.parser.start(self)

	def _find_resources(self):
		self._pull_dbtune()
		
		# hier mit Fallback anfangen

		# print (not self.dbtuneURL)

		if not self.dbtuneURL:
			print ("[-] Could not find Resource on DBTune => Trying with musicbrainz dump now")
			self._pull_mbdump()
			if not self.musicbrainzID and self.manualQuery:
				print ("[-] Could not find Resource on musicbrainz-dump => Trying with original Input now")
				self.name = self.input
				self._pull_dbtune()
				if not self.dbtuneURL:
					print ("[-] Could not find Resource on DBTune with original input => Trying with musicbrainz dump now")
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
		if not self.images:
			self._pull_commons()
		return self.images

	def has_images(self):
		self.get_images()
		return len(self.images) > 0 and self.images[0] != "None"

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

				    print "Neues BILD!"
				    print result["url"]["value"]
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
			# self.dbtune_set = -1
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
		if not self.spotifyID:
			print("[~] Pulling Spotify ID")
			self.spotifyID = self._pull_spotify_id()
		return self.spotifyID

	def _pull_spotify_id(self):
		try:
			if self.dbtune_set == 1:
				self.spotifyID = self.get_echoNestArtist().get_foreign_id('spotify')
			return self.spotifyID
		except:
			print "[!] Error fetching spotifyID"


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

		# Voting starts here

		self._vote()

		# Parsing starts here

		# self.parser.start(self)

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

			if self.currentMembers or self.soloArtist:
				self._pull_current_bands_of_current_members()
				self._pull_former_bands_of_current_members()
				self._pull_writer_relation_of_current_members()
				self._pull_producer_relation_of_current_members()

			if self.formerMembers:
				self._pull_current_bands_of_former_members()
				self._pull_former_bands_of_former_members()
				self._pull_producer_relation_of_former_members()
				self._pull_writer_relation_of_former_members()

			self._pull_further_urls()
			self._pull_discogs()
			self._pull_musixmatch()
			self._pull_discogs_artist()

		except:
			pass

		if self.state == 0:
			print("[+] done")
			for artist in self.recommendation:
				print "Artist: "+artist.get_name()+" has Vote: ",artist.get_vote()
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
			if self.echoNestArtist:
				return self.echoNestArtist
		else:
			return self.echoNestArtist

	def _pull_echoNest_artist(self):
		if self.musicbrainzID:
			self.echoNestArtist = artist.Artist('musicbrainz:artist:'+self.musicbrainzID)
			if self.echoNestArtist:
				print("[+] pulled echoNestArtist")
			else:
				print("[-] Could not find echoNestArtist")
		else:
			return -1

	def get_discogsArtist(self):
		if not self.discogsArtist and self.state == 0:
			print("[~] pulling discogsArtist")
			self._pull_discogs_artist()
			if self.discogsArtist:
				return self.discogsArtist
		else:
			return self.discogsArtist

	def _pull_discogs_artist(self):
		print("[~] Trying to pull discogs artist")
		if self.discogs_url:
			self.discogsArtist = d.artist(self.discogsID)
			if self.discogsArtist:
				print("[+] pulled discogsArtist")
			else:
				print("[-] Could not find discogsArtist")
		else:
			return -1

	def _pull_further_urls(self):
		print("[~] Trying to pull Further Urls")
		
		self.further_urls = self.get_echoNestArtist().get_urls()
		if not self.further_urls:
			print("[-] Could not find further URLs")
		else:
			print("[+] Found further URLs")

			if 'official_url' in self.further_urls:
				self.official = self.further_urls[u'official_url']
				print ("[+] Offizielle Website: "+self.official)
			if 'lastfm_url' in self.further_urls:
				self.lastfm = self.further_urls[u'lastfm_url']
				print ("[+] Last Fm: "+self.lastfm)
			if 'wikipedia_url' in self.further_urls:
				self.wikipedia = self.further_urls[u'wikipedia_url']
				print ("[+] Wikipedia: "+self.wikipedia)
			if 'myspace_url' in self.further_urls:
				self.myspace = self.further_urls[u'myspace_url']
				print ("[+] Myspace: "+self.myspace)
			if 'twitter_url' in self.further_urls:
				self.twitter = self.further_urls[u'twitter_url']
				print ("[+] Twitter: "+self.twitter)
				self.twitterUsername = self.twitter[20:]

	def get_discogs(self):
		if not self.discogs:
			self._pull_discogs()
		if self.discogs:
			return self.discogs

	def _pull_discogs(self):
		try:
			print("[~] Trying to pull discogs")
			self.discogs = self.get_echoNestArtist().get_foreign_id('discogs')
			if self.discogs:
				print("[+] Found Discogs Resource: "+ self.discogs)
				self.convert_discogs_to_url()

			else: 
				print("[-] Could not find discogs")
		except:
			pass

	def convert_discogs_to_url(self):
		self.discogsID = self.discogs[15:]
		self.discogs_url = "http://www.discogs.com/artist/"+self.discogsID
		print("[+] discogs-url: "+self.discogs_url)

	# ========================================================================================
	# MUSIXMATCH get and _pull
	# ========================================================================================

	def get_musixmatch(self):
		if not self.musixmatch:
			self._pull_musixmatch()
		if self.musixmatch:
			return self.musixmatch

	def _pull_musixmatch(self):
		try:
			print("[~] Trying to pull musixmatch")
			self.musixmatch = self.get_echoNestArtist().get_foreign_id('musixmatch-WW')
			if self.musixmatch:
				print("[+] Found musixmatch Resource: "+ self.musixmatch)
				self.convert_musixmatch_to_url()

			else: 
				print("[-] Could not find musixmatch")
		except:
			pass

	def convert_musixmatch_to_url(self):
		self.musixmatch_url = "https://www.musixmatch.com/artist/"+self.musixmatch[21:]
		print("[+] musixmatch-url: "+self.musixmatch_url)

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
				temp = [self.eventsJSON["resultsPage"]["results"]["event"][i]["displayName"], self.eventsJSON["resultsPage"]["results"]["event"][i]["uri"]]
				self.events.append(temp)
		else:
			temp = ["No Concerts found.", ""]
			self.events.append(temp)

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
				elif 'List_of' not in result["member"]["value"]:
					self.currentMembersNR.append(result["member"]["value"])
					print("[-] No Resource on dbpedia for: "+result["member"]["value"])
				else:
					print("[-] Found 'List of Members'-Resource, did not add it to members")

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
						self.formerMembers.append(result["member"]["value"])
						print result["member"]["value"]
					elif 'List_of' not in result["member"]["value"]:
						self.formerMembersNR.append(result["member"]["value"])
						print("[-] No Resource on dbpedia for: "+result["member"]["value"])
					else:
						print("[-] Found 'List of Members'-Resource, did not add it to members")
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
				elif 'List_of' not in result["member"]["value"]:
					self.formerMembersNR.append(result["member"]["value"])
					print("[-] No Resource on dbpedia for: "+result["member"]["value"])
				else:
					print("[-] Found 'List of Members'-Resource, did not add it to members")
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
					elif 'List_of' not in result["member"]["value"]:
						self.formerMembersNR.append(result["member"]["value"])
						print("[-] No Resource on dbpedia for: "+result["member"]["value"])
					else:
						print("[-] Found 'List of Members'-Resource, did not add it to members")
		except:
			print ("[-] error while pulling former members")

	# ===============================================================
	# TODO ERROR-HANDLING
	# 			ab hier untegesteter code ohne error handling
	# ===============================================================

	def _pull_producer_relation_of_current_members(self):
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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMproducer, "Because "+self._uri_to_name(member)+" was active as producer"))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was active as producer")
							knownArtist.addVote(cMproducer)

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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMproducer, "Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as producer"))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as producer")
							knownArtist.addVote(cMproducer)
		except:
			print ("[-] error while pulling producer relation for current members")

	def _pull_producer_relation_of_former_members(self):
		try:
			for member in self.formerMembers:
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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], fMproducer, "Because "+self._uri_to_name(member)+" was active as producer"))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was active as producer")
							knownArtist.addVote(fMproducer)
		except:
			print ("[-] error while pulling producer relation for former members")

	def _pull_writer_relation_of_current_members(self):
		try:
			for member in self.currentMembers:
				print ("[~] searching writer realtion of current member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?artist WHERE {
		    			?work dbprop:writer <"""+member+""">.
		    			?work dbpedia-owl:artist ?artist
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["artist"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["artist"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["artist"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["artist"]["value"], cMwriter, "Because "+self._uri_to_name(member)+" was active as writer."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was active as writer.")
							knownArtist.addVote(cMwriter)

			if self.soloArtist:
				print ("[~] searching writer realtion of maybe solo-artist: "+ self.get_dbpediaURL())
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?artist WHERE {
		    			?work dbprop:writer <"""+self.get_dbpediaURL()+""">.
		    			?work dbpedia-owl:artist ?artist.
		    			}
					""")
				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["artist"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["artist"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["artist"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["artist"]["value"], cMwriter, "Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as writer."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" was active as writer.")
							knownArtist.addVote(cMwriter)
		except:
			print ("[-] error while pulling writer relation for current members")

	def _pull_writer_relation_of_current_members(self):
		try:
			for member in self.formerMembers:
				print ("[~] searching writer realtion of current member: "+ member)
				sparql = SPARQLWrapper("http://dbpedia.org/sparql")
				sparql.setQuery("""
					PREFIX dbprop: <http://dbpedia.org/property/>
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

					SELECT DISTINCT ?artist WHERE {
		    			?work dbprop:writer <"""+member+""">.
		    			?work dbpedia-owl:artist ?artist
		    			}
					""")

				sparql.setReturnFormat(JSON)
				results = sparql.query().convert()	
				for result in results["results"]["bindings"]:
					if result["artist"]["value"] != self.get_dbpediaURL() and 'List_of' not in result["artist"]["value"]:
						new = True
						knownArtist = None
						for r in self.recommendation:
							if result["artist"]["value"] == r.get_dbpediaURL():
								print ("DEBUG: Not a new Artist: "+r.get_dbpediaURL())
								knownArtist = r
								new = False
						if new:
							self.recommendation.append(MusicMashupArtist(result["artist"]["value"], fMwriter, "Because "+self._uri_to_name(member)+" was active as writer."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was active as writer.")
							knownArtist.addVote(fMwriter)
		except:
			print ("[-] error while pulling writer relation for former members")

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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMcurrentBandVote, "Because "+self._uri_to_name(member)+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" is also a member of this band.")
							knownArtist.addVote(cMcurrentBandVote)
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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMcurrentBandVote, "Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band.")
							knownArtist.addVote(cMcurrentBandVote)
		except:
			print ("[-] error while pulling cuurent band of current member")

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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMformerBandVote,"Because "+self._uri_to_name(member)+" was also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was also a member of this band.")
							knownArtist.addVote(cMformerBandVote)

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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], cMformerBandVote, "Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(self.get_dbpediaURL())+" is also a member of this band.")
							knownArtist.addVote(cMformerBandVote)
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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], fMcurrentBandVote, "Because "+self._uri_to_name(member)+" is also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" is also a member of this band.")
							knownArtist.addVote(fMcurrentBandVote)
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
							self.recommendation.append(MusicMashupArtist(result["band"]["value"], fMformertBandVote, "Because "+self._uri_to_name(member)+" was also a member of this band."))
						else:
							knownArtist.addReason("Because "+self._uri_to_name(member)+" was also a member of this band.")
							knownArtist.addVote(fMformertBandVote)
		except:
			print ("[-] error while pulling former bands of former members")	

	def _uri_to_name(self, uri):
		# print("[~] Converting URI to name")
		uri = uri[28:]
		uri = uri.replace('_', ' ')
		# uri = urllib.unquote_plus(uri)
		return uri

	def uri_to_name_if_necessary(self, uri):
		if uri[:4] == "http":
			return self._uri_to_name(uri)
		else:
			return uri

	def quote_anything(self, anything):
		return urllib.quote_plus(anything)

	def addReason(self, reason):
		self.reason.append(reason)

	def addVote(self, voteValue):
		print ("[+] VOTE INCREASED BY: ",voteValue)
		self.vote += voteValue
		print ("[+] Vote is now: ", self.vote)

	def get_vote(self):
		return self.vote

	# ========================================================================================
	# VOTING
	# ========================================================================================

	def _vote(self):
		voteValue = []
		for r in self.recommendation:
			voteValue.append(r.get_vote())
		length = len(self.recommendation)
		for i in range(0, length):
			for j in range(0, length-1):
				if voteValue[j] < voteValue[j+1]:
					temp = self.recommendation[j]
					self.recommendation[j] = self.recommendation[j+1]
					self.recommendation[j+1] = temp
					temp = voteValue[j]
					voteValue[j] = voteValue[j+1]
					voteValue[j+1] = temp
		print ("After Sorting: ")
		for artist in self.recommendation:
			print "Artist: "+artist.get_name()+" has Vote: ",artist.get_vote()


	def current_load_time(self):
		return time.clock()-self.starttime

# run from console for test setup
if __name__ == '__main__':
	test = MusicMashupArtist("Page and Plant")
	print("this is a test.")
	print(test.get_name())
	print(test.get_abstract())
	print(test.get_spotify_id())
	test.get_images()
	# print(test.get_abstract())
	# print(test.dbtuneURL)
	# print (test.dbpediaURL)
	#blubb = test.get_related()
	# print(blubb)
	#for r in blubb:
#		print(" + "+r.get_name() + " - " + r.get_abstract_excerpt(50) + " - " + r.get_spotify_id())
	print(test.has_images())
