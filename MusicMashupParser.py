# -*- coding: utf-8 -*-

class MusicMashupParser:

	def __init__(self):
		self.artist = None		

	def start(self, artistObject):
		self.artist = artistObject

	def parse_to_rdf(self):
		filename = self.artist.get_name().lower().replace(' ', '_')
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
		file.write("<"+self.artist.dbpediaURL()+"> dbpedia-owl:abstract \""+self.artist.abstract+"\" .\n")
	
	def parse_current_members(self, file):
		if self.artist.currentMembers:
			for member in self.artist.currentMembers:
				file.write("<"+self.artist.get_dbpediaURL()+"> dbprop:currentMember <"+member+"> .\n")

	def parse_related_artists(self, file):
		if self.artist.relatedSources:
			for artist in self.artist.relatedSources:
				file.write("<"+self.artist.get_dbpediaURL()+"> dbpedia-owl:associatedMusicalArtist <"+artist+"> .\n")