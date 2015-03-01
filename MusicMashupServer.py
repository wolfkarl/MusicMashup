#### this is the server class as well as the starter script for MusicMashup.

# server is build upon cherrypy
import cherrypy
import os

# the actual program logic is handled by the artist class
from MusicMashupArtist import MusicMashupArtist

# template engine
from mako.template import Template
from mako.lookup import TemplateLookup


# used for history / breadcrumbs generation
from urllib import quote_plus
# to make band names pretty in breadcrumbs
from titlecase import titlecase

class MusicMashupServer(object):

	def __init__(self):
		pass


	@cherrypy.expose # tell cherrypy to map this function on "/" URL
	def index(self, query="", soloartist=0):

		# initialize mako (template engine)
		lookup = TemplateLookup(directories=['html'])
		
		# show search page if no query has been made
		if query == "":
			print "[~] No query given, serving search page"
			tmpl = lookup.get_template("search.htm")
			return tmpl.render()

		# query is present. could be a dbpedia URL or text search, artist class will deal with that
		else: 

			### create musicmashup object based on query. this handles everything but the breadcrumbs.
			self.artist = MusicMashupArtist(query)

			### save things to breadcrumbs and prepare them to be shown on the page

			# add new query to breadcrumbs list. create as list if not existing yet
			if not "history" in cherrypy.session:
				cherrypy.session['history'] = []

			# new search -> new breadcrumbs
			if not query[:4] == "http": # if it's not a URL, it must be text search
				cherrypy.session['history'] = [] # reset history list

				# also, if name rather than query, convert to titlecase
				query = titlecase(query)

			# append newest query to list, template will determine if it's a URI or name
			if not (len(cherrypy.session['history']) > 0 and cherrypy.session['history'][-1] == query):
				cherrypy.session['history'].append(query)

			# load mako templates
			tmpl = lookup.get_template("main.htm")

			# add whole Artist object and history array from sessions
			# all queries etc. will be triggered from within the template.
			# basically, all information is fetched "on demand" by the artist object
			return tmpl.render(artist=self.artist, history=cherrypy.session['history'])		

 


# End of class

#### Startup script

if __name__ == '__main__':
	print ("[~] Initializing...")

	# configure cherrypy entity, especially turn on session handling and define ./static 
	# as the folder to serve images, css etc.

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

    # start the server based on the functions of the MM-Server class
	cherrypy.quickstart(MusicMashupServer(), '/', conf)