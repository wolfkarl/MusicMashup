import cherrypy
import os
from MusicMashup import MusicMashup
from mako.template import Template
from mako.lookup import TemplateLookup

class MusicMashupServer(object):

	def __init__(self):
		# locate templates
		pass


	@cherrypy.expose # wird von cherrypy auf eine URL gemappt
	def index(self, query="Alexander Marcus Experience"):

		# create musicmashup object based on query:
		self.mm = MusicMashup(query)
		lookup = TemplateLookup(directories=['html'])
		tmpl = lookup.get_template("main.htm")
		return tmpl.render(query = query, desc=self.mm.description())


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