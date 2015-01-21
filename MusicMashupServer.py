# server shizzle
import cherrypy
import os

# eigentliche arbeit macht die artist klasse
from MusicMashupArtist import MusicMashupArtist

# template gedoens
from mako.template import Template
from mako.lookup import TemplateLookup

# fuer history generation
from urllib import quote_plus

class MusicMashupServer(object):

	def __init__(self):
		pass


	@cherrypy.expose # wird von cherrypy auf eine URL gemappt
	def index(self, query="Queens of the Stone Age"):

		# create musicmashup object based on query:
		self.artist = MusicMashupArtist(query)

		# add new query to breadcrumbs list. create as list if not present
		if not "history" in cherrypy.session:
			cherrypy.session['history'] = []

		# append newest query to list, template will determine if it's a URI or name
		cherrypy.session['history'].append(query)

		# make sure the list has no more than 5 entries
		maxentries = 5
		if len(cherrypy.session['history']) > maxentries:
			cherrypy.session['history'].pop


		# load mako templates
		lookup = TemplateLookup(directories=['html'])
		tmpl = lookup.get_template("main.htm")

		# add whole Artist object and history array from sessions
		return tmpl.render(artist=self.artist, history=cherrypy.session['history'])		

 


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