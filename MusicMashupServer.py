import cherrypy
import os
from MusicMashupArtist import MusicMashupArtist
from mako.template import Template
from mako.lookup import TemplateLookup

class MusicMashupServer(object):

	def __init__(self):
		pass


	@cherrypy.expose # wird von cherrypy auf eine URL gemappt
	def index(self, query="Queens of the Stone Age"):

		# create musicmashup object based on query:
		self.artist = MusicMashupArtist(query)
		lookup = TemplateLookup(directories=['html'])
		tmpl = lookup.get_template("main.htm")
		return tmpl.render(artist=self.artist)		
		# return tmpl.render(
		# 		query 		= self.artist.get_name(), 
		# 		abstract	= self.artist.get_abstract(),
		# 		spotify_uri	= self.artist.get_spotify_uri()
		# 		)
 


# End of class

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