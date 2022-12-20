from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.namespace._XSD import XSD
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from uuid import uuid4 as uuid


CC = Namespace("http://creativecommons.org/ns#")
DOAJ = Namespace("https://doaj.org/")
FABIO = Namespace("http://purl.org/spar/fabio/")
FC = Namespace("https://fatcat.wiki/")
ISSN = Namespace("https://issn.org/")
LOC = Namespace("http://id.loc.gov/ontologies/bibframe/")
PAD = Namespace("https://journalobservatory.org/pad/")
OPENALEX = Namespace("https://docs.openalex.org/about-the-data/venue#")
PPO = Namespace("https://purl.org/cwts/ppo/")
PRISM = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
PRO = Namespace("http://purl.org/spar/pro/")
RDFG = Namespace("http://www.w3.org/2004/03/trix/rdfg-1/")
ROMEO = Namespace("https://v2.sherpa.ac.uk/id/")
SCHEMA = Namespace("https://schema.org/")
SCHEMA1 = Namespace("http://schema.org/")
STM = Namespace("https://osf.io/7j6ck/")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
WIKIBASE = Namespace("http://wikiba.se/ontology#")
DCTERMS = DCTERMS
XSD = XSD
RDF = RDF
RDFS = RDFS


class PADNamespaceManager(NamespaceManager):
    def __init__(self, this=None):
        super().__init__(Graph())
        self.bind("cc", CC)
        self.bind("doaj", DOAJ)
        self.bind("fabio", FABIO)
        self.bind("fc", FC)
        self.bind("issn", ISSN)
        self.bind("pad", PAD)
        self.bind("ppo", PPO)
        self.bind("loc", LOC)
        self.bind("openalex", OPENALEX)
        self.bind("prism", PRISM)
        self.bind("pro", PRO)
        self.bind("romeo", ROMEO)
        self.bind("rdfg", RDFG)
        self.bind("schema1", SCHEMA1)
        self.bind("stm", STM)
        self.bind("wd", WD)
        self.bind("wdt", WDT)
        self.bind("wikibase", WIKIBASE)
        self.bind_this(this=this)

    def bind_this(self, this=None):
        if not this:
            this = PAD + str(uuid())
        self.THIS = Namespace(this)
        self.SUB = Namespace(self.THIS + "/")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)
