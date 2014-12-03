""" Launches an HTTP server using cherrypy and handles requests to the MusicMashupServer class """

import cherrypy # v.3.6.0 https://pypi.python.org/pypi/CherryPy
from MusicMashupServer import MusicMashupServer


print ("[~] Initializing...")
# bind to all IPv4 interfaces
cherrypy.config.update({'server.socket_host': '0.0.0.0'})

cherrypy.quickstart(MusicMashupServer())