import os
from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from rdflib.namespace._RDF import RDF as rdf
from uuid import uuid4 as uuid


JOB = Namespace("https://job.org/")
JOBMAP = Namespace("https://job.org/jobmap/")
DOAJ = Namespace("https://doaj.org/")
ROMEO = Namespace("https://v2.sherpa.ac.uk/id/")
LOCAL = Namespace(f"file://{os.getcwd()}/")
SCHEMA = Namespace("https://schema.org/")
ISSN = Namespace("https://issn.org/")
CC0 = Namespace("https://creativecommons.org/publicdomain/zero/")
CC = Namespace("https://creativecommons.org/licenses/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
global RDF
RDF = rdf

class JobNamespace(NamespaceManager):
    def __init__(self, uuid=False):
        super().__init__(Graph())
        self.bind("job", JOB)
        self.bind("jobmap", JOBMAP)
        self.bind("doaj", DOAJ)
        self.bind("romeo", ROMEO)
        self.bind("local", LOCAL)
        self.bind("schema", SCHEMA)
        self.bind("issn", ISSN)
        self.bind("cc0", CC0)
        self.bind("cc", CC)
        self.bind("xsd", XSD)
        if uuid:
            self.bind_uuid()

    def bind_uuid(self):
        id = "https://job.org/jobmap/" + str(uuid())
        self.THIS = Namespace(id)
        self.SUB = Namespace(id + "#")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)
