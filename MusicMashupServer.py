# server shizzle
import cherrypy
import os

# eigentliche arbeit macht die artist klasse
from MusicMashupArtist import MusicMashupArtist

# template gedoens
from mako.template import Template
from mako.lookup import TemplateLookup
from titlecase import titlecase

# fuer history generation
from urllib import quote_plus

class MusicMashupServer(object):

	def __init__(self):
		pass


	@cherrypy.expose # wird von cherrypy auf eine URL gemappt
	def index(self, query="", soloartist=0):
		# initialize mako (template engine)
		lookup = TemplateLookup(directories=['html'])
		
		# show search page if no query has been made
		if query == "":
			print "[~] No query given, serving search page"
			tmpl = lookup.get_template("search.htm")
			return tmpl.render()

		# query is present
		else: 
			# create musicmashup object based on query:
			self.artist = MusicMashupArtist(query)

			# add new query to breadcrumbs list. create as list if not present
			if not "history" in cherrypy.session:
				cherrypy.session['history'] = []

			# new search -> new breadcrumbs
			if not query[:4] == "http":
				cherrypy.session['history'] = []

				# also, if name rather than query, convert to titlecase
				query = titlecase(query)

			# append newest query to list, template will determine if it's a URI or name
			if not (len(cherrypy.session['history']) > 0 and cherrypy.session['history'][-1] == query):
				cherrypy.session['history'].append(query)

			# make sure the list has no more than 5 entries
			maxentries = 10
			if len(cherrypy.session['history']) > maxentries:
				cherrypy.session['history'].pop


			# load mako templates
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