# -*- coding: utf-8 -*-

class MusicMashupParser:

	def __init__(artistName):
		self.artistName = artistName
		self.parse_to_rdf()

	def parse_to_rdf():
			filename = self.artistName.lower().replace(' ', '_')
			filepath = "dumps/"+filename
			# fileExists = os.path.exists(filepath)
			
			file = open(filepath, 'w+')
			
			self.parse_prefixes(file)
			self.parse_abstract(file)
			self.parse_current_members(file)
			
			self.parse_related_artists(file)
			file.close()
		
		def parse_prefixes(file):
			file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
			file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
			file.write("@prefix mo: <http://purl.org/ontology/mo/> .\n")
			file.write("@prefix dbpedia-owl: <http://dbpedia.org/ontology/> .\n")
			file.write("@prefix dbprop: <http://dbpedia.org/property/> .\n")
			file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
		
		def parse_abstract(file):
			file.write("<"+self.get_dbpediaURL()+"> dbpedia-owl:abstract \""+self.abstract+"\" .\n")
		
		def parse_current_members(file):
			for member in self.currentMembers:
				file.write("<"+self.get_dbpediaURL()+"> dbprop:currentMember <"+member+"> .\n")
		def parse_related_artists(file):
			for artist in self.relatedSources:
				file.write("<"+self.get_dbpediaURL()+"> dbpedia-owl:associatedMusicalArtist <"+artist+"> .\n")