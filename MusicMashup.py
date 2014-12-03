""" Hauptklasse, wird erzeugt fuer jede Suchanfrage und stellt dann die Informationen ueber verschiedene Subklassen bereit """
class MusicMashup:

	def __init__(self, query):
		self.query = query

	def description(self):
		return self.query + " is a post-progressive powerviolence core supergroup with massive destruction elements."

	def upcoming_tours(self):
		pass