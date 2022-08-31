from configparser import ConfigParser
from glob import glob
from namespace import JobNamespace
from pyparsing.exceptions import ParseException
from rdflib import URIRef
from store import json_to_graph
from tqdm import tqdm as progress
from utils.graph import init_graph
from utils.utils import file_to_json, ROOT_DIR
import json
import re

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
        

def graph_to_jobmap(graph, queries):
    jobnamespace = JobNamespace(uuid=True)
    jobmap_graph = init_graph(nm=jobnamespace)
    graph.namespace_manager = jobnamespace
    # graph.bind("this", jobnamespace.THIS, override=True)
    # graph.bind("sub", jobnamespace.SUB, override=True)

    for query in queries:
        try:
            jobmap_graph += graph.query(query)
        except(ParseException) as e:
            print(f"Error during parsing:\n\n{query}\n")
            raise(e)
    return jobmap_graph


def json_to_jobmap(journal_json, context, queries):
    graph = json_to_graph(journal_json, context)
    return graph_to_jobmap(graph, queries)


def json_file_to_jobmap(file, context_file, queries_file):
    journal_json = file_to_json(file)
    context = file_to_json(context_file)
    queries = read_query_file(queries_file)
    return json_to_jobmap(journal_json, context, queries)
        

def dataset_convert(dataset, batchsize=100):
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    context_file = config.get(dataset, "context_file")
    convert_file = config.get(dataset, "convert_file")
    bulk_path = config.get(dataset, "bulk_path")
    db_type = config.get("job", "db_type")
    db_path = config.get("job", "db_path")

    context = file_to_json(context_file)
    queries = read_query_file(convert_file)
    files = glob(f"{bulk_path}/data/*.json")

    if config.getboolean("main", "test", fallback=False):
        return dataset_convert_test(files, context, queries, dataset)

    graph_id = URIRef(f"https://job.org/jobmap/{dataset}")
    jobmap_graph = init_graph(db_type, db_path, id=graph_id)
    jobmap_graph.create_graph()
    jobmap_graph.clear()

    for n in progress(range(0, len(files), batchsize), unit_scale=batchsize):
        jobmap = init_graph()
        for file in files[n:n+batchsize]:
            sherpa_romeo_record = file_to_json(file)
            jobmap += json_to_jobmap(sherpa_romeo_record, context, queries)
        jobmap_graph.insert_graph(jobmap)
    return jobmap_graph


def dataset_convert_test(files, context, queries, dataset, item=0):
    record = file_to_json(files[item])
    jobmap = json_to_jobmap(record, context, queries)
    with open(f"{ROOT_DIR}/test/{dataset}_record.json", "w") as f:
        json.dump(record, f, indent=4)
    jobmap.serialize(f"{ROOT_DIR}/test/{dataset}_jobmap.ttl", format="turtle")
    json_to_graph(record, context).serialize(f"{ROOT_DIR}/test/{dataset}_graph.ttl", format="turtle")
    return jobmap
