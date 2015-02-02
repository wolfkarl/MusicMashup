import rdflib
import rdfextras
rdfextras.registerplugins() 

defaultValue = 0.5


class MusicMashupPagerank(object):


	def __init__(self):
		self.mygraph = rdflib.Graph()
		print ("[*] Starting to parse pagerank-turtle-file")
		self.mygraph.parse('data/pagerank.ttl', format='n3')
		print ("[*] Finished parsing")

	def get_pagerank(self, resource):
		pagerank = None
		if resource != -1:
			print ("[~] Querying Pagerank for: "+resource)
			try:
				results = self.mygraph.query("""
					PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
					SELECT DISTINCT ?rank WHERE {
					<"""+resource+"""> dbpedia-owl:wikiPageRank ?rank

					}
				""")
				for row in results:
					pagerank = row[0]
			except:
				pass


		if pagerank:
			print "[+] Found Pagerank: ", pagerank
			return float(pagerank)
		else:
			print ("[-] Did not find Pagerank, returning default Value")
			return defaultValue

# paggy = MusicMashupPagerank()
# paggy.get_pagerank("http://dbpedia.org/resource/The_Bakerton_Group")