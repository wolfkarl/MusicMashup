import rdflib
from rdflib.term import URIRef

g = rdflib.Graph()
result = g.parse("http://www.bbc.co.uk/nature/life/Clupeiformes")

print("graph has %s statements." % len(g))
# prints graph has 79 statements.

for subj, pred, obj in g:
   if (subj, pred, obj) not in g:
       raise Exception("It better be!")

s = g.serialize(format='n3')

print s