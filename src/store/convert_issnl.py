from tqdm import tqdm as progress
from utils.namespace import PADNamespaceManager, PAD, PPO, DCTERMS, FABIO, PRISM, XSD
from utils.graph import pad_graph
from rdflib import Literal, URIRef
from rdflib.namespace._RDF import RDF
from store.convert import pad_add_creation_docinfo
from utils.store import sparql_store
from store.bulk_issnl import get_issnl_file, issnl_parse_bulk_file
from os import path


def issnl_tuple_to_pad(issnl, issn, date):
    jobnamespace = PADNamespaceManager()
    pad = pad_graph(nm=jobnamespace)
    platform = URIRef(f"https://issn.org/{issnl}")
    THIS = pad.namespace_manager.THIS[""]
    SUB = pad.namespace_manager.SUB
    pad.add((THIS, RDF.type, PAD.PAD, SUB.docinfo))
    pad.add((THIS, PAD.hasAssertion, SUB.assertion, SUB.docinfo))
    pad.add((THIS, PAD.hasProvenance, SUB.provenance, SUB.docinfo))

    pad.add((SUB.assertion, DCTERMS.license, URIRef("https://creativecommons.org/publicdomain/zero/1.0/"), SUB.provenance))
    pad.add((SUB.assertion, DCTERMS.created, Literal(date, datatype=XSD.date), SUB.provenance))
    pad.add((SUB.assertion, DCTERMS.creator, URIRef("https://issn.org"), SUB.provenance))
    
    pad.add((platform, RDF.type, PPO.Platform, SUB.assertion))
    pad.add((platform, PRISM.issn, Literal(issn), SUB.assertion))
    pad.add((platform, FABIO.hasIssnL, Literal(issnl), SUB.assertion))
    return pad


def dataset_convert_issnl(file, limit=None, batchsize=100):
    file_base = path.basename(file)
    date = f"{file_base[:4]}-{file_base[4:6]}-{file_base[6:8]}"
    bulk = issnl_parse_bulk_file(file, identicals=False)
    sparqlstore = sparql_store(update=True)
    if not limit: limit = len(bulk)
    if batchsize > limit: batchsize = limit
    for n in progress(range(0, limit, batchsize), unit_scale=batchsize):
        batchgraph = pad_graph()
        for issnl, issn in bulk[n:n+batchsize]:
            pad = issnl_tuple_to_pad(issnl, issn, date)
            pad_add_creation_docinfo(pad, config)
            batchgraph.addN(pad.quads())
        sparqlstore.addN(batchgraph.quads())


if __name__ == "__main__":
    from utils.utils import job_config as config

    bulk_dir = config.get("issnl", "bulk_path", fallback="~/issnl")
    file = get_issnl_file(bulk_dir)
    number = config.getint("issnl", "limit", fallback=None)
    batchsize = config.getint("issnl", "batchsize", fallback=500)

    if config.getboolean("main", "test", fallback=False):
        raise(Exception("No test function for convert_issnl"))
