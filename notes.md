
There are two datatypes in RDF. This may or may not be the official jargon:

URIs reference some conceptual entity. They are usualy written like you see web addresses but surrounded in < > brackets, as in <http://people.csail.mit.edu/eob#ted>. Note that the < > brackets do not represent an XML tag – you don’t need to backslash it as a singleton, liks so: <br />. The brackets are just to dilineate the URI.

Literals are literal datatypes — strings, ints, etc. Literals should enclosed in quotes but may be typed with a ^^ operator. Literals are usually typed by XSD datatypes but don’t have to be.


Triples are the atomic block of expression in RDF. They are always represented by:

    A subject, which must be a URI (called a Resource in this sense)
    A property, which must be a URI (called a Property in this sense)
    An object, which can be either a URI (called a Resource in this sense) or a literal



**RDF/Turtle Einführung**
http://haystack.csail.mit.edu/blog/2008/11/06/a-quick-tutorial-on-the-tutrle-rdf-serialization/