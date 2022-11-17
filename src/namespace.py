from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from uuid import uuid4 as uuid


CC = Namespace("http://creativecommons.org/ns#")
DOAJ = Namespace("https://doaj.org/")
FABIO = Namespace("http://purl.org/spar/fabio/")
ISSN = Namespace("https://issn.org/")
LOC = Namespace("http://id.loc.gov/ontologies/bibframe/")
MAP = Namespace("https://journalobservatory.org/map/")
OPENALEX = Namespace("https://openalex.org/")
PPO = Namespace("https://purl.org/cwts/ppo/")
PRISM = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
PRO = Namespace("http://purl.org/spar/pro/")
RDFG = Namespace("http://www.w3.org/2004/03/trix/rdfg-1/")
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
        self.bind("ppo", PPO)
        self.bind("loc", LOC)
        self.bind("openalex", OPENALEX)
        self.bind("prism", PRISM)
        self.bind("pro", PRO)
        self.bind("romeo", ROMEO)
        self.bind("rdfg", RDFG)
        self.bind("schema", SCHEMA)
        self.bind("stm", STM)
        if uuid:
            self.bind_uuid()

    def bind_uuid(self):
        self.THIS = Namespace(MAP + str(uuid()))
        self.SUB = Namespace(self.THIS + "#")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)

    def namespace_bindings(self):
        bindings = {}
        for bind, ns in self.namespaces():
            bindings[bind] = ns
        return bindings
