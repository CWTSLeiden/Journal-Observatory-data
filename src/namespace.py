from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from uuid import uuid4 as uuid


CC = Namespace("http://creativecommons.org/ns#")
DOAJ = Namespace("https://doaj.org/")
FABIO = Namespace("http://purl.org/spar/fabio/")
ISSN = Namespace("https://issn.org/")
JOB = Namespace("https://job.org/")
JOBMAP = Namespace("https://job.org/jobmap/")
LOC = Namespace("http://id.loc.gov/ontologies/bibframe/")
OPENALEX = Namespace("https://openalex.org/")
PPR = Namespace("https://job.org/peer_review/")
PRISM = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
PRO = Namespace("http://purl.org/spar/pro/")
ROMEO = Namespace("https://v2.sherpa.ac.uk/id/")
SCHEMA = Namespace("https://schema.org/")
STM = Namespace("https://osf.io/68rnz/")

class JobNamespace(NamespaceManager):
    def __init__(self, uuid=False):
        super().__init__(Graph())
        self.bind("cc", CC)
        self.bind("doaj", DOAJ)
        self.bind("fabio", FABIO)
        self.bind("issn", ISSN)
        self.bind("job", JOB)
        self.bind("jobmap", JOBMAP)
        self.bind("loc", LOC)
        self.bind("openalex", OPENALEX)
        self.bind("ppr", PPR)
        self.bind("prism", PRISM)
        self.bind("pro", PRO)
        self.bind("romeo", ROMEO)
        self.bind("schema", SCHEMA)
        self.bind("stm", STM)
        if uuid:
            self.bind_uuid()

    def bind_uuid(self):
        id = "https://job.org/jobmap/" + str(uuid())
        self.THIS = Namespace(id)
        self.SUB = Namespace(id + "#")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)

    def namespace_bindings(self):
        bindings = {}
        for bind, ns in self.namespaces():
            bindings[bind] = ns
        return bindings
