import glob
import csv
from tqdm import tqdm as progress
from utils.namespace import *
from rdflib.namespace import DCTERMS
from utils.graph import job_graph
from rdflib import Literal, URIRef
from rdflib.namespace._RDF import RDF
from store.convert import jobmap_add_info
from utils.store import sparql_store

def load_issnl_file(bulk_dir):
    "Obtain the right file from the bulk import directory."
    file = glob.glob(f"{bulk_dir}/*ISSN-to-ISSN-L.txt")
    try:
        return file[0]
    except IndexError:
        print("ISSN-to-ISSN-L.txt file not found. Please obtain it from https://issn.org")
        print(f"and store it in {bulk_dir}/")
        return ""


def line_to_issnl(line, identicals=True):
    "Transform a line from the bulk file into a issn-l,issn tuple."
    if line.get("ISSN") and line.get("ISSN-L"):
        if not identicals and (line.get("ISSN") == line.get("ISSN-L")):
            return None
        return (line.get("ISSN-L"), line.get("ISSN"))
    return None


def issnl_parse_bulk_file(bulk_dir, identicals=True):
    """
    Convert the bulk file into a set
    parameters:
        identicals: include records in the list where issnl == issn
    """
    store = []
    file = load_issnl_file(bulk_dir)
    if file and progress:
        with open(file, "r") as f:
            for line in progress(csv.DictReader(f, delimiter='\t'), desc="Parse bulk file"):
                t = line_to_issnl(line, identicals)
                if t:
                    store.append(t)
    return store


def issnl_tuple_to_jobmap(issnl, issn, date):
    jobnamespace = JobNamespace()
    jobmap = job_graph(nm=jobnamespace)
    platform = URIRef(f"https://issn.org/{issnl}")
    THIS = jobnamespace.THIS[""]
    SUB = jobnamespace.SUB
    jobmap.add((THIS, RDF.type, PPO.PAD, SUB.head))
    jobmap.add((THIS, PPO.hasAssertion, SUB.assertion, PPO.head))
    jobmap.add((THIS, PPO.hasProvenance, SUB.provenance, PPO.head))

    jobmap.add((SUB.assertion, CC.license, URIRef("https://creativecommons.org/publicdomain/zero/1.0/"), SUB.provenance))
    jobmap.add((SUB.assertion, DCTERMS.created, Literal(date, datatype=SCHEMA.Date), SUB.provenance))
    jobmap.add((SUB.assertion, DCTERMS.creator, URIRef("https://issn.org"), SUB.provenance))
    
    jobmap.add((platform, RDF.type, PPO.Platform, SUB.assertion))
    jobmap.add((platform, PRISM.issn, Literal(issn), SUB.assertion))
    jobmap.add((platform, FABIO.hasIssnL, Literal(issnl), SUB.assertion))
    return jobmap


def dataset_convert_issnl():
    from configparser import ConfigParser
    from utils.utils import ROOT_DIR
    from os import path

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    bulk_dir = config.get("issnl", "bulk_path", fallback="~/issnl")

    file = path.basename(load_issnl_file(bulk_dir))
    date = f"{file[:4]}-{file[4:6]}-{file[6:8]}"

    if config.getboolean("main", "test", fallback=False):
        raise(Exception("No test function for convert_issnl"))

    bulk = issnl_parse_bulk_file(bulk_dir, identicals=False)
    sparqlstore = sparql_store(update=True)
    batchsize = 500
    number = config.getint("issnl", "limit", fallback=len(bulk))
    if batchsize > number: batchsize = number
    for n in progress(range(0, number, batchsize), unit_scale=batchsize):
        batchgraph = job_graph()
        for issnl, issn in bulk[n:n+batchsize]:
            jobmap = issnl_tuple_to_jobmap(issnl, issn, date)
            jobmap_add_info(jobmap, config)
            batchgraph.addN(jobmap.quads())
        sparqlstore.addN(batchgraph.quads())


if __name__ == "__main__":
    dataset_convert_issnl()
