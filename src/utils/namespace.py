from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DefinedNamespace, NamespaceManager
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.namespace._XSD import XSD
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from uuid import uuid4 as uuid

class PPO(DefinedNamespace):
    _NS = Namespace("https://purl.org/cwts/ppo/")
    Accessible: URIRef
    ArticlePublishingCharges: URIRef
    AuthorEditorCommunication: URIRef
    EvaluationPolicy: URIRef
    NotAccessible: URIRef
    OptIn: URIRef
    Platform: URIRef
    PlatformType: URIRef
    Policy: URIRef
    PublicAccessability: URIRef
    PublicationElsewhereAllowedPolicy: URIRef
    PublicationElsewhereMandatoryPolicy: URIRef
    PublicationElsewherePolicy: URIRef
    PublicationElsewhereProhibitedPolicy: URIRef
    PublicationPolicy: URIRef
    ReviewReport: URIRef
    ReviewSummary: URIRef
    SubmittedManuscript: URIRef
    anonymousTo: URIRef
    appliesToVersion: URIRef
    covers: URIRef
    hasArticlePublishingCharges: URIRef
    hasCopyrightOwner: URIRef
    hasFatcatId: URIRef
    hasInitiator: URIRef
    hasOpenalexId: URIRef
    hasPlatformType: URIRef
    hasPolicy: URIRef
    hasSherpaRomeoId: URIRef
    identityPubliclyAccessible: URIRef
    interactsWith: URIRef
    involves: URIRef
    isOpenAccess: URIRef
    optInBy: URIRef
    postPublicationCommenting: URIRef
    postPublicationCommentingClosed: URIRef
    postPublicationCommentingOnInvitation: URIRef
    postPublicationCommentingOpen: URIRef
    publicationCondition: URIRef
    publiclyAccessible: URIRef

class PAD(DefinedNamespace):
    _NS = Namespace("https://journalobservatory.org/pad/")
    PAD: URIRef
    Assertion: URIRef
    Provenance: URIRef
    PubInfo: URIRef
    hasAssertion: URIRef
    hasSourceAssertion: URIRef
    hasProvenance: URIRef
    hasPubInfo: URIRef
    hasProvenance: URIRef

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
    def __init__(self, this=None):
        super().__init__(Graph())
        self.bind("cc", CC)
        self.bind("doaj", DOAJ)
        self.bind("dcterms", DCTERMS)
        self.bind("fabio", FABIO)
        self.bind("fc", FC)
        self.bind("issn", ISSN)
        self.bind("pad", PAD)
        self.bind("ppo", PPO)
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
            this = PAD + str(uuid())
        self.THIS = Namespace(this)
        self.SUB = Namespace(self.THIS + "/")
        self.bind("this", self.THIS)
        self.bind("sub", self.SUB)
