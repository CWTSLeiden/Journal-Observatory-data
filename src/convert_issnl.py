import glob
import csv
from tqdm import tqdm as progress
from namespace import *
from utils.graph import init_graph
from rdflib import Literal, URIRef

def load_issnl_file(bulk_dir):
    "Obtain the right file from the bulk import directory."
    file = glob.glob(f"{bulk_dir}/*ISSN-to-ISSN-L.txt")
    try:
        return file[0]
    except IndexError:
        print("ISSN-to-ISSN-L.txt file not found. Please obtain it from https://issn.org")
        print(f"and store it in {bulk_dir}/")
        return ""


def line_to_issnl(line, filter=None):
    "Transform a line from the bulk file into a issn-l,issn tuple."
    if line.get("ISSN") and line.get("ISSN-L"):
        if not filter or line.get("ISSN") in filter:
            return (line.get("ISSN-L"), line.get("ISSN"))
    return None


def issnl_parse_bulk_file(bulk_dir, filter=None):
    """
    Convert the bulk file into a set
    parameters:
        filter: A list of issns to be included in the store
        location: An alternative location for the resulting csv-file
            (default: [import].[db] from config)
    """
    store = []
    file = load_issnl_file(bulk_dir)
    if file and progress:
        with open(file, "r") as f:
            for line in progress(csv.DictReader(f, delimiter='\t'), desc="Parse bulk file"):
                t = line_to_issnl(line, filter)
                if t:
                    store.append(t)
    return store


def issnl_tuple_to_jobmap(issnl, issn, date):
    jobnamespace = JobNamespace(uuid=True)
    jobmap = init_graph(nm=jobnamespace)
    THIS = jobnamespace.THIS
    SUB = jobnamespace.SUB
    creationdate = Literal(date, datatype=SCHEMA.Date)
    jobmap.add((THIS.self, RDF.type, JOB.JobMap))
    jobmap.add((THIS.self, JOB.hasDataLicense, CC0["1.0"]))
    jobmap.add((THIS.self, JOB.hasCreationDate, creationdate))
    jobmap.add((THIS.self, JOB.hasDataSource, URIRef("https://issn.org")))
    jobmap.add((THIS.self, JOB.hasAssertion, SUB.identifier))
    jobmap.add((SUB.identifier, RDF.type, JOB.IdentifierAssertion))
    jobmap.add((SUB.identifier, FABIO.issn, Literal(issn)))
    jobmap.add((SUB.identifier, FABIO.hasIssnL, Literal(issnl)))
    return jobmap


if __name__ == "__main__":
    from configparser import ConfigParser
    from utils.utils import ROOT_DIR
    from os import path

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    db_type = config.get("job", "db_type")
    db_path = config.get("job", "db_path")

    bulk_dir = config.get("issnl", "bulk_path", fallback="~/issnl")
    file = path.basename(load_issnl_file(bulk_dir))
    date = f"{file[:4]}-{file[4:6]}-{file[6:8]}"

    jobmap_graph = init_graph(db_type, db_path, id=URIRef("https://job.org/jobmap/issnl"))
    try:
        jobmap_graph.clear()
    except:
        pass

    batchsize = 500
    bulk = issnl_parse_bulk_file(bulk_dir)
    for n in progress(range(0, len(bulk), batchsize), unit_scale=batchsize):
        jobmap = init_graph()
        for issnl, issn in bulk[n:n+batchsize]:
            jobmap += issnl_tuple_to_jobmap(issnl, issn, date)
        jobmap_graph.insert_graph(jobmap)
