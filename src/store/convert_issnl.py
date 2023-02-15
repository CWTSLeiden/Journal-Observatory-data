if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from bulk.bulk_issnl import get_issnl_file, issnl_parse_bulk_file
from os import path
from rdflib import Literal, URIRef, Dataset
from store.convert import batch_convert, pad_add_creation_docinfo
from utils import pad_config as config
from utils.namespace import PAD, PPO, DCTERMS, FABIO, PRISM, XSD, RDF
from utils.pad import PADGraph
from utils.print import print_verbose


def issnl_tuple_to_pad(issnl, issn, date):
    pad = PADGraph()
    platform = URIRef(f"https://issn.org/{issnl}")
    THIS = pad.THIS
    SUB = pad.SUB
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


def convert_issnl(db : Dataset, debug=False):
    print_verbose("Convert dataset: issnl")
    dataset_config = config["issnl"]

    data_path = dataset_config.getpath("data_path", fallback="data/issnl")
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=500)
    file = get_issnl_file(data_path)
    creator_id = config.get("main", "identifier", fallback="")

    if debug:
        print_verbose("No test function for convert_issnl")
        return False
    file_base = path.basename(file)
    date = f"{file_base[:4]}-{file_base[4:6]}-{file_base[6:8]}"
    try:
        bulk = issnl_parse_bulk_file(file, identicals=False)
        if limit:
            bulk = bulk[:limit]
        def record_to_pad(record : tuple[str, str]):
            issnl, issn = record
            pad = issnl_tuple_to_pad(issnl, issn, date)
            pad = pad_add_creation_docinfo(pad, creator_id)
            return pad
        batch_convert(db, bulk, record_to_pad, batchsize)
    except FileNotFoundError:
        print(f"No file found at {file}")
        return False
    return True


if __name__ == "__main__":
    from utils.store import sparql_store_config
    debug = config.getboolean("main", "debug", fallback=False)
    convert_issnl(sparql_store_config(config, update=True), debug)
