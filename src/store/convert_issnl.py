from bulk.bulk_issnl import get_issnl_file, issnl_parse_bulk_file
from os import path
from rdflib import Literal, URIRef
from store.convert import batch_convert
from utils import job_config as config
from utils.graph import pad_graph
from utils.namespace import PADNamespaceManager, PAD, PPO, DCTERMS, FABIO, PRISM, XSD, RDF
from utils.print import print_verbose


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


def convert_issnl(debug=False):
    print_verbose("Convert dataset: issnl")
    dataset_config = config["issnl"]

    bulk_dir = dataset_config.get("bulk_path", fallback="~/issnl")
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=500)
    file = get_issnl_file(bulk_dir)
    creator_id = config.get("main", "identifier", fallback=None)

    if debug:
        print_verbose("No test function for convert_issnl")
        return False
    file_base = path.basename(file)
    date = f"{file_base[:4]}-{file_base[4:6]}-{file_base[6:8]}"
    bulk = issnl_parse_bulk_file(file, identicals=False)
    def record_to_pad(record : tuple[str, str]):
        issnl, issn = record
        return issnl_tuple_to_pad(issnl, issn, date)
    batch_convert(bulk, record_to_pad, limit, batchsize, creator_id)
    return True

