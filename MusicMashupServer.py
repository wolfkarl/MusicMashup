import cherrypy
import os
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


if __name__ == '__main__':
	print ("[~] Initializing...")
	# bind to all IPv4 interfaces
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	conf = {
    	'/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }

	cherrypy.quickstart(MusicMashupServer(), '/', conf)