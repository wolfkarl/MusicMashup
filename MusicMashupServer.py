import cherrypy
from MusicMashup import MusicMashup

class MusicMashupServer(object):

	def __init__(self):
		pass

	@cherrypy.expose # wird von cherrypy auf eine URL gemappt
	def index(self, query="Alexander Marcus Experience"):

		# create musicmashup object based on query:
		self.mm = MusicMashup(query)

		text = "<h1>Music Mashup: " + self.mm.query + "</h1>"
		text += "<p>" + self.mm.description() + "</p>"
		return text