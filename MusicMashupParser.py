# -*- coding: utf-8 -*-

import codecs
import os
import time
import datetime

# This is the implementation of a parser.
# We tried using rdflib to parse the information but it somehow didn't work.
# So we decided to write our own parser.

class MusicMashupParser:

	def __init__(self):
		self.artist = None
		self.baseArtist = ""		

# start get's called by the MusicMashupArtist in order to commence parsing
# in order to let the parser access the information, an artist object passes itself		

	def start(self, artistObject):
		self.artist = artistObject
		self.baseArtist = ":" + str(self.artist.get_name().replace(' ', '_'))
		filename = self.artist.get_name().lower().replace(' ', '_').replace('/', '') + ".ttl"
		filepath = "dumps/"+filename
		# checking whether the last dump is older than a week
		if os.path.exists(filepath):
			creationTime = os.path.getctime(filepath)
			nowTime = time.time()
			oneWeek = 60*60*24*7 # number of seconds in a week
			print ("CREATED AT: "+str(creationTime))
			print ("NOW IT'S: "+str(time.time()))
			print (nowTime - oneWeek)
			if nowTime > creationTime + oneWeek:
				self._parse_to_rdf(filepath)
			else:
				print ("[-] The dump is younger than one week. No new dump will be created.")
		else:
			self._parse_to_rdf(filepath)

	def _parse_to_rdf(self, filepath):
		
		file = codecs.open(filepath, 'w+', 'utf-8')
		
		self._parse_prefixes(file)
		self._parse_abstract(file)
		self._parse_current_members(file)
		self._parse_former_members(file)
		self._parse_thumbnail(file)
		self._parse_images(file)
		self._parse_same_as(file)
		self._parse_see_also(file)
		self._parse_related_artists(file)
		self._parse_events(file)
		self._parse_api_keys(file)

		file.close()
		
	def _parse_prefixes(self, file):
		file.write("@base dbpedia-owl: <http://dbpedia.org/resource/> .\n")
		file.write("@prefix mm: <localhost/ontology/musicmashup>")
		file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
		file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
		file.write("@prefix mo: <http://purl.org/ontology/mo/> .\n")
		file.write("@prefix dbprop: <http://dbpedia.org/property/> .\n")
		file.write("@prefix foaf: <http://xmlns.com/foaf/0.1/Image> .\n")
		file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
	
	def _parse_abstract(self, file):
		if self.artist.abstract:	
			file.write(self.baseArtist+" dbpedia-owl:abstract \""+self.artist.get_abstract().encode('ascii', 'replace')+"\" .\n")
	
	def _parse_current_members(self, file):
		if self.artist.currentMembers:
			for member in self.artist.currentMembers:
				file.write(self.baseArtist+" dbpedia-owl:currentMember :"+member[28:]+" .\n")

	def _parse_former_members(self, file):
		if self.artist.formerMembers:
			for member in self.artist.formerMembers:
				file.write(self.baseArtist+" dbpedia-owl:formerMember :"+member[28:]+" .\n")

	def _parse_thumbnail(self, file):
		if self.artist.thumbnail:
			file.write(self.baseArtist+" dbpedia-owl:thumbnail <"+self.artist.thumbnail+"> .\n")

	def _parse_images(self, file):
		if self.artist.images:
			for image in self.artist.images:
				file.write(self.baseArtist+" foaf:Image <"+image+"> .\n")

	def _parse_same_as(self, file):
		if self.artist.dbtuneURL:
			file.write(self.baseArtist+" owl:sameAs <"+str(self.artist.get_dbtuneURL())+"> .\n")
		if self.artist.musicbrainzID:
			file.write(self.baseArtist+" owl:sameAs <http://musicbrainz.org/artist/"+str(self.artist.musicbrainzID)+"> .\n")
		if self.artist.dbpediaCommonsURL:
			file.write(self.baseArtist+" owl:sameAs <"+str(self.artist.dbpediaCommonsURL)+"> .\n")

	def _parse_see_also(self, file):
		if self.artist.discogs_url:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.discogs_url+"> .\n")
		if self.artist.musixmatch_url:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.musixmatch_url+"> .\n")
		if self.artist.official:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.official+"> .\n")
		if self.artist.lastfm:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.lastfm+"> .\n")
		if self.artist.wikipedia:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.wikipedia+"> .\n")
		if self.artist.myspace:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.myspace+"> .\n")
		if self.artist.twitter:
			file.write(self.baseArtist+" rdfs:seeAlso <"+self.artist.twitter+"> .\n")

	def _parse_related_artists(self, file):
		if self.artist.recommendation:
			for artist in self.artist.recommendation:
				file.write(self.baseArtist+" mm:recommendedArtist :"+artist.get_name().replace(' ', '_')+" .\n")
				file.write(":"+artist.get_name().replace(' ', '_')+" mm:voteValue "+str(artist.vote)+" .\n")
				file.write(":"+artist.get_name().replace(' ', '_')+" mm:echonestFamiliarity "+str(artist.get_familiarity(justGet=True))+" .\n")
				file.write(":"+artist.get_name().replace(' ', '_')+" dbpedia-owl:wikiPageRank "+str(artist.get_pagerank())+" .\n")
				for reason in artist.reason:
					prop = self._decode_reason(reason)
					member = self._get_name_from_reason(reason)
					file.write(":"+member.replace(' ', '_') + " " + prop + " :" + artist.get_name().replace(' ', '_') + " .\n")

	def _parse_api_keys(self, file):
		if self.artist.musicbrainzID:
			file.write(self.baseArtist+" mm:musicbrainzID \""+self.artist.musicbrainzID+"\" .\n")
		if self.artist.spotifyID:
			file.write(self.baseArtist+" mm:spotifyID \""+self.artist.spotifyID+"\" .\n")
		if self.artist.echoNestArtist:
			file.write(self.baseArtist+" mm:echonestArtist \""+str(self.artist.echoNestArtist)+"\" .\n")

	def _parse_events(self, file):
		if self.artist.events:
			for event in self.artist.events:
				file.write(self.baseArtist+" mm:songkickEvent \""+event[1]+"\" .\n")

	def _decode_reason(self, reason):
		if "writer" in reason:
			return "dbpedia-owl:writer"
		elif "producer" in reason:
			return "dbpedia-owl:producer"
		elif "composer" in reason:
			return "dbpedia-owl:composer"
		elif "member" in reason:
			if "is" in reason:
				return "dbpedia-owl:currentMember"
			else:
				return "dbpedia-owl:formerMember"
		else:
			return ":WRONG"

	def _get_name_from_reason(self, reason):
		reason = reason.replace('Because ', '')
		reason = reason.replace(' was ', '')
		reason = reason.replace('active', '')
		reason = reason.replace(' as ', '')
		reason = reason.replace('writer.', '')
		reason = reason.replace('producer', '')
		reason = reason.replace('composer.', '')
		reason = reason.replace(' is ', '')
		reason = reason.replace('also', '')
		reason = reason.replace(' a ', '')
		reason = reason.replace('member', '')
		reason = reason.replace(' of', '')
		reason = reason.replace(' this', '')
		reason = reason.replace(' band.', '')
		return reason

