# -*- coding: utf-8 -*-

class MusicMashupParser:

	def __init__(self):
		self.artist = None
		self.baseArtist = ""		

	def start(self, artistObject):
		self.artist = artistObject
		self.baseArtist = ":" + str(self.artist.get_name().replace(' ', '_'))
		print ("THIS WILL BE PARSED AS BASEARTIST: "+self.baseArtist)
		self.parse_to_rdf()

	def parse_to_rdf(self):
		filename = self.artist.get_name().lower().replace(' ', '_') + ".ttl"
		filepath = "dumps/"+filename
		# fileExists = os.path.exists(filepath)
		
		file = open(filepath, 'w+')
		
		self.parse_prefixes(file)
		self.parse_abstract(file)
		self.parse_current_members(file)
		self.parse_former_members(file)
		self.parse_thumbnail(file)
		self.parse_images(file)
		self.parse_same_as(file)
		self.parse_see_also(file)
		self.parse_related_artists(file)
		self.parse_api_keys(file)

		file.close()
		
	def parse_prefixes(self, file):
		file.write("@base dbpedia-owl: <http://dbpedia.org/ontology/> .\n")
		file.write("@prefix mm: <localhost/ontology/musicmashup>")
		file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
		file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
		file.write("@prefix mo: <http://purl.org/ontology/mo/> .\n")
		file.write("@prefix dbprop: <http://dbpedia.org/property/> .\n")
		file.write("@prefix foaf: <http://xmlns.com/foaf/0.1/Image> .\n")
		file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
	
	def parse_abstract(self, file):
		if self.artist.abstract:	
			file.write(self.baseArtist+" dbpedia-owl:abstract \""+self.artist.get_abstract().encode('ascii', 'replace')+"\" .\n")
	
	def parse_current_members(self, file):
		if self.artist.currentMembers:
			for member in self.artist.currentMembers:
				file.write(self.baseArtist+" :currentMember :"+member[28:]+" .\n")

	def parse_former_members(self, file):
		if self.artist.formerMembers:
			for member in self.artist.formerMembers:
				file.write(self.baseArtist+" :formerMember :"+member[28:]+" .\n")

	def parse_thumbnail(self, file):
		if self.artist.thumbnail:
			file.write(self.baseArtist+" dbpedia-owl:thumbnail <"+self.artist.thumbnail+"> .\n")

	def parse_images(self, file):
		if self.artist.images:
			for image in self.artist.images:
				file.write(self.baseArtist+" foaf:Image <"+image+"> .\n")

	def parse_same_as(self, file):
		if self.artist.dbtuneURL:
			file.write(self.baseArtist+" owl:sameAs <"+self.artist.get_dbtuneURL()+"> .\n")
		if self.artist.musicbrainzID:
			file.write(self.baseArtist+" owl:sameAs <http://musicbrainz.org/artist/"+str(self.artist.musicbrainzID)+"> .\n")
		if self.artist.dbpediaCommonsURL:
			file.write(self.baseArtist+" owl:sameAs <"+str(self.artist.dbpediaCommonsURL)+"> .\n")

	def parse_see_also(self, file):
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

	def parse_related_artists(self, file):
		if self.artist.recommendation:
			for artist in self.artist.recommendation:
				file.write(self.baseArtist+" mm:recommendedArtist :"+artist.get_name().replace(' ', '_')+" .\n")
				for reason in artist.reason:
					prop = self._decode_reason(reason)
					member = self._get_name_from_reason(reason)
					file.write(":"+member.replace(' ', '_') + " " + prop + " " + self.baseArtist + " .\n")

	def parse_api_keys(self, file):
		if self.artist.musicbrainzID:
			file.write(self.baseArtist+" mm:musicbrainzID \""+self.artist.musicbrainzID+"\" .\n")
		if self.artist.spotifyID:
			file.write(self.baseArtist+" mm:spotifyID \""+self.artist.spotifyID+"\" .\n")
		if self.artist.echoNestArtist:
			file.write(self.baseArtist+" mm:echonestArtist \""+str(self.artist.echoNestArtist)+"\" .\n")


	def _decode_reason(self, reason):
		if "writer" in reason:
			return ":writer"
		elif "producer" in reason:
			return ":producer"
		elif "member" in reason:
			if "is" in reason:
				return ":currentMember"
			else:
				return ":formerMember"
		else:
			return ":WRONG"

	def _get_name_from_reason(self, reason):
		reason = reason.replace('Because ', '')
		reason = reason.replace(' was ', '')
		reason = reason.replace('active', '')
		reason = reason.replace(' as ', '')
		reason = reason.replace('writer.', '')
		reason = reason.replace('producer', '')
		reason = reason.replace(' is ', '')
		reason = reason.replace('also', '')
		reason = reason.replace(' a ', '')
		reason = reason.replace('member', '')
		reason = reason.replace(' of', '')
		reason = reason.replace(' this', '')
		reason = reason.replace(' band.', '')
		# print ("HIER SOLLTE NUR EIN NAME STEHEN::"+reason)
		return reason

