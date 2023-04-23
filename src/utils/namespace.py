from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.namespace._XSD import XSD
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from uuid import uuid4 as uuid

SCPO = Namespace("http://purl.org/job/scpo/")
PAD = Namespace("http://purl.org/job/pad/")
PAD_PREFIX = Namespace("https://journalobservatory.org/pad/")
JOB_PREFIX = Namespace("https://journalobservatory.org/job/pad/")

CC = Namespace("http://creativecommons.org/ns#")
DOAJ = Namespace("https://doaj.org/")
FABIO = Namespace("http://purl.org/spar/fabio/")
FC = Namespace("https://fatcat.wiki/")
ISSN = Namespace("https://issn.org/")
LOC = Namespace("http://id.loc.gov/ontologies/bibframe/")
OPENALEX = Namespace("https://docs.openalex.org/about-the-data/venue#")
PRISM = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
PRO = Namespace("http://purl.org/spar/pro/")
PSO = Namespace("http://purl.org/spar/pso/")
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
    def __init__(self, this=None, prefix=PAD_PREFIX):
        super().__init__(Graph())
        self.PREFIX = prefix
        self.bind("cc", CC)
        self.bind("doaj", DOAJ)
        self.bind("dcterms", DCTERMS)
        self.bind("fabio", FABIO)
        self.bind("fc", FC)
        self.bind("issn", ISSN)
        self.bind("jobid", JOB_PREFIX)
        self.bind("padid", PAD_PREFIX)
        self.bind("pad", PAD)
        self.bind("scpo", SCPO)
        self.bind("loc", LOC)
        self.bind("openalex", OPENALEX)
        self.bind("prism", PRISM)
        self.bind("pro", PRO)
        self.bind("pso", PSO)
        self.bind("romeo", ROMEO)
        self.bind("rdfg", RDFG)
        self.bind("schema", SCHEMA)
        self.bind("schema1", SCHEMA1)
        self.bind("stm", STM)
        self.bind("wd", WD)
        self.bind("wdt", WDT)
        self.bind("wikibase", WIKIBASE)
        self.bind_this(this=this)

    def bind_this(self, this=None):
        if not this:
            this = self.PREFIX + str(uuid())
        self.THIS = Namespace(this)
        self.SUB = Namespace(self.THIS + "/")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)
