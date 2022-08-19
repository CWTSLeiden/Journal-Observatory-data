import re
from namespace import JobNamespace
from issnl_store import ISSNL_Store
from utils import init_graph

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

    doaj_graph.bind("this", jobnamespace.THIS, override=True)
    doaj_graph.bind("sub", jobnamespace.SUB, override=True)
    doaj_graph += issnl_from_graph(doaj_graph, issnl_store)

    queries = read_query_file(query_file)
    for query in queries:
        jobmap_graph += doaj_graph.query(query)

    return jobmap_graph
        

def test():
    from configparser import ConfigParser
    from utils import ROOT_DIR
    import os

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    issnl_db = config.get("issnl", "db_path")
    convert_file = config.get("doaj", "convert_file")
    db_path = config.get("doaj", "db_path")

    issnl_store = ISSNL_Store(db=issnl_db)

    doaj_graph = init_graph()
    doaj_graph.parse(os.path.join(db_path, "doaj.ttl"))

    jobmap_graph = convert(doaj_graph, convert_file, issnl_store)

    jobmap_graph.serialize(os.path.join(db_path, "jobmap.ttl"), format="turtle")
    jobmap_graph.serialize(os.path.join(db_path, "jobmap.json"), format="json-ld", auto_compact=True)

test()
