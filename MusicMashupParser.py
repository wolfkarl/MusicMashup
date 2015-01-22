# -*- coding: utf-8 -*-

class MusicMashupParser:

	def __init__(self):
		self.artist = None		

	def start(self, artistObject):
		self.artist = artistObject
		print (type(self.artist.get_abstract()))
		self.parse_to_rdf()

	def parse_to_rdf(self):
		filename = self.artist.get_name().lower().replace(' ', '_')
		filepath = "dumps/"+filename
		# fileExists = os.path.exists(filepath)
		
		file = open(filepath, 'w+')
		
		self.parse_prefixes(file)
		self.parse_abstract(file)
		self.parse_current_members(file)
		self.parse_former_members(file)
		self.parse_related_artists(file)
		self.parse_thumbnail(file)
		self.parse_images(file)
		self.parse_same_as(file)
		self.parse_see_also(file)

		file.close()
		
	def parse_prefixes(self, file):
		file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
		file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
		file.write("@prefix mo: <http://purl.org/ontology/mo/> .\n")
		file.write("@prefix dbpedia-owl: <http://dbpedia.org/ontology/> .\n")
		file.write("@prefix dbprop: <http://dbpedia.org/property/> .\n")
		file.write("@prefix foaf: <http://xmlns.com/foaf/0.1/Image> .\n")
		file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
	
	def parse_abstract(self, file):
		if self.artist.abstract:	
			file.write("<"+self.artist.get_dbpediaURL().encode('ascii', 'replace')+"> dbpedia-owl:abstract \""+self.artist.get_abstract().encode('ascii', 'replace')+"\" .\n")
		## encode('ascii', 'replace') ist ein ziemlich harter workaround.
		## Der Parser wirft eine UnicodeDecodeError Exception, wenn merkwürdige Sonderzeichen kommen (die nebenbei gesagt komplett fehl am Platz sind...)
	
	def parse_current_members(self, file):
		if self.artist.currentMembers:
			for member in self.artist.currentMembers:
				file.write("<"+self.artist.get_dbpediaURL()+"> dbprop:currentMember <"+member.encode('ascii', 'replace')+"> .\n")

	def parse_former_members(self, file):
		if self.artist.formerMembers:
			for member in self.artist.formerMembers:
				file.write("<"+self.artist.get_dbpediaURL()+"> dbprop:currentMember <"+member.encode('ascii', 'replace')+"> .\n")

	def parse_related_artists(self, file):
		if self.artist.recommendation:
			for artist in self.artist.recommendation:
				file.write("<"+self.artist.get_dbpediaURL()+"> dbpedia-owl:associatedMusicalArtist <"+artist.get_dbpediaURL().encode('ascii', 'replace')+"> .\n")

	def parse_thumbnail(self, file):
		if self.artist.thumbnail:
			file.write("<"+self.artist.get_dbpediaURL()+"> dbpedia-owl:thumbnail <"+self.artist.thumbnail+"> .\n")

	def parse_images(self, file):
		if self.artist.images:
			for image in self.artist.images:
				file.write("<"+self.artist.get_dbpediaURL()+"> foaf:Image <"+image+"> .\n")

	def parse_same_as(self, file):
		if self.artist.dbtuneURL:
			file.write("<"+self.artist.get_dbpediaURL()+"> owl:sameAs <"+self.artist.get_dbtuneURL()+"> .\n")
		if self.artist.musicbrainzID:
			file.write("<"+self.artist.get_dbpediaURL()+"> owl:sameAs <http://musicbrainz.org/artist/"+str(self.artist.musicbrainzID)+"> .\n")
		if self.artist.dbpediaCommonsURL:
			file.write("<"+self.artist.get_dbpediaURL()+"> owl:sameAs <"+str(self.artist.dbpediaCommonsURL).encode('ascii', 'replace')+"> .\n")

	def parse_see_also(self, file):
		if self.artist.discogs_url:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.discogs_url+"> .\n")
		if self.artist.musixmatch_url:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.musixmatch_url+"> .\n")
		if self.artist.official:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.official.encode('ascii', 'replace')+"> .\n")
		if self.artist.lastfm:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.lastfm+"> .\n")
		if self.artist.wikipedia:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.wikipedia+"> .\n")
		if self.artist.myspace:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.myspace+"> .\n")
		if self.artist.twitter:
			file.write("<"+self.artist.get_dbpediaURL()+"> rdfs:seeAlso <"+self.artist.twitter+"> .\n")