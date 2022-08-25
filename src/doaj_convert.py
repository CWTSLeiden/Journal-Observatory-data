import re
from namespace import JobNamespace
from issnl_store import ISSNL_Store
from utils import *
from glob import glob

def issnl_from_graph(graph, issnl_store : ISSNL_Store):
    query = """
        select ?issn
        where {
            ?journal ?issntype ?issn .
            filter (?issntype in (schema:pissn, schema:eissn))
        }
    """
    issns = [row[0].value for row in graph.query(query)]
    issnl_graph = issnl_store.open_graph(filter=issns)
    return issnl_graph


def read_query_file(file):
    queries = []
    with open(file, "r") as query_file:
        querylines = query_file.read().split("\n")
    querylines = [ q for q in querylines if not re.search("^ *(#.*)?$", q) ]
    n = -1
    for line in querylines:
        if re.search("^construct ", line) or n < 0:
            n += 1; queries.append("")
        queries[n] += " " + line
    return queries
        

def convert(doaj_graph, query_file, issnl_store):
    jobnamespace = JobNamespace(uuid=True)
    jobmap_graph = init_graph(nm=jobnamespace)
    # print(f"this: {jobnamespace.THIS}")

    jobmap_graph.bind("this", jobnamespace.THIS, override=True)
    jobmap_graph.bind("sub", jobnamespace.SUB, override=True)
    doaj_graph.bind("this", jobnamespace.THIS, override=True)
    doaj_graph.bind("sub", jobnamespace.SUB, override=True)
    # doaj_graph += issnl_from_graph(doaj_graph, issnl_store)

    queries = read_query_file(query_file)
    for query in queries:
        jobmap_graph = add_to_graph(jobmap_graph, doaj_graph.query(query))

    return jobmap_graph
        

def test():
    from configparser import ConfigParser
    from utils import ROOT_DIR

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    issnl_db = config.get("issnl", "db_path")
    convert_file = config.get("doaj", "convert_file")
    bulk_path = config.get("doaj", "bulk_path")
    files = glob(f"{bulk_path}/rdf/*.ttl")

    # issnl_store = ISSNL_Store(db=issnl_db)
    # issnl_store.open()
    issnl_store = None

    jobmap_graph = init_graph()

    for n, f in enumerate(files[:4]):
        doaj_graph = init_graph()

        doaj_graph.parse(f)

        jobmap_graph = add_to_graph(jobmap_graph, convert(doaj_graph, convert_file, issnl_store))

    jobmap_graph.serialize("jobmap.ttl", format="turtle")
test()
