from configparser import ConfigParser
from glob import glob
from utils.namespace import JobNamespace, PPO
from pyld import jsonld
from pyparsing.exceptions import ParseException
from rdflib import DCTERMS, URIRef, Literal, XSD
from tqdm import tqdm as progress
from utils.graph import job_graph
from utils.jsonld import jsonld_frame, jobmap_frame, jsonld_strip
from utils.print import print_verbose
from utils.store import sparql_store
from utils.utils import file_to_json, ROOT_DIR
import datetime
import json
import re


def add_context(record, context={}):
    "Add the @context from the context file to the record"
    context_record = record.copy()
    for prefix, namespace in JobNamespace().namespaces():
        if not context.get(prefix):
            context[prefix] = namespace
    context_record["@context"] = context
    context_record["@type"] = "http://www.w3.org/2004/03/trix/rdfg-1/Graph"
    return context_record


def jsonld_to_graph(record, graph=None):
    """
    Convert a json-ld record to an rdf graph
    If graph is provided, add to the existing graph
    """
    if not graph: graph = job_graph()
    record = jsonld.compact(record, record["@context"])
    graph.parse(data=json.dumps(record), format='json-ld')
    return graph


def json_to_graph(journal_json, context={}, graph=None, serialize=None):
    "Convert a json record to a graph."
    if not graph: graph = job_graph()
    journal_jsonld = add_context(journal_json, context)
    graph = jsonld_to_graph(journal_jsonld, graph)
    if serialize:
        graph.serialize(destination=serialize)
    return graph


def read_query_file(file):
    queries = []
    with open(file, "r") as query_file:
        querylines = query_file.read().split("\n")
    querylines = [ q for q in querylines if not re.search("^ *(#.*)?$", q) ]
    n = -1
    for line in querylines:
        if re.search("^(construct|insert|select) ", line) or n < 0:
            n += 1; queries.append("")
        queries[n] += " " + line
    return queries


def graph_to_jobmap(graph, queries, clean=True):
    jobnamespace = JobNamespace()
    graph.namespace_manager = jobnamespace
    original_graphs = list(graph.contexts())
    for query in queries:
        try:
            graph.update(query)
        except(ParseException) as e:
            print(f"Error during parsing:\n\n{query}\n")
            raise(e)

    if clean:
        for original_graph in original_graphs:
            graph.remove_context(original_graph)
    return graph


def json_to_jobmap(journal_json, context, queries):
    graph = json_to_graph(journal_json, context)
    return graph_to_jobmap(graph, queries, clean=True)


def json_file_to_jobmap(file, context_file, queries_file):
    journal_json = file_to_json(file)
    context = file_to_json(context_file)
    queries = read_query_file(queries_file)
    return json_to_jobmap(journal_json, context, queries)


def jobmap_add_info(jobmap, config):
    config.read(f"{ROOT_DIR}/config/job.conf")
    identifier = config.get("main", "identifier")
    license = config.get("main", "license")
    date = datetime.date.today()
    THIS = jobmap.namespace_manager.THIS[""]
    SUB = jobmap.namespace_manager.SUB
    jobmap.add((THIS, DCTERMS.license, URIRef(license), SUB.docinfo))
    jobmap.add((THIS, DCTERMS.creator, URIRef(identifier), SUB.docinfo))
    jobmap.add((THIS, DCTERMS.created, Literal(date ,datatype=XSD.date), SUB.docinfo))
    jobmap.add((THIS, PPO.hasDocInfo, SUB.docinfo, SUB.head))
    return jobmap
        

def dataset_convert(dataset, batchsize=100):
    print_verbose(f"Convert dataset: {dataset}")
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    context_file = config.get(dataset, "context_file")
    convert_file = config.get(dataset, "convert_file")
    bulk_path = config.get(dataset, "bulk_path")

    context = file_to_json(context_file)
    queries = read_query_file(convert_file)
    files = glob(f"{bulk_path}/data/*.json")

    if config.getboolean("main", "test", fallback=False):
        item = config.getint(dataset, "test_item", fallback=0)
        return dataset_convert_test(dataset, files=files, context=context, queries=queries, item=item)

    sparqlstore = sparql_store(update=True)
    number = config.getint(dataset, "limit", fallback=len(files))
    if batchsize > number: batchsize = number
    for n in progress(range(0, number, batchsize), unit_scale=batchsize):
        batchgraph = job_graph()
        for file in files[n:n+batchsize]:
            record = file_to_json(file)
            jobmap = json_to_jobmap(record, context, queries)
            jobmap = jobmap_add_info(jobmap, config)
            batchgraph.addN(jobmap.quads())
        sparqlstore.addN(batchgraph.quads())


def dataset_convert_test(dataset, files=None, context=None, queries=None, item=0):
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")

    if not context:
        context_file = config.get(dataset, "context_file")
        context = file_to_json(context_file)
    if not queries:
        convert_file = config.get(dataset, "convert_file")
        queries = read_query_file(convert_file)
    if not files:
        bulk_path = config.get(dataset, "bulk_path")
        files = glob(f"{bulk_path}/data/*.json")

    record = file_to_json(files[item])
    jobmap = json_to_jobmap(record, context, queries)
    jobmap = jobmap_add_info(jobmap, config)
    datagraph = json_to_graph(record, context)
    # Write record to file
    print(f"Write record to file:")
    print(f" - test/{dataset}_record.json")
    with open(f"{ROOT_DIR}/test/{dataset}_record.json", "w") as f:
        json.dump(record, f, indent=4)
    # Write converted graph to file
    print(f"Write data graph to file:")
    print(f" - test/{dataset}_graph.ttl")
    datagraph.serialize(f"{ROOT_DIR}/test/{dataset}_graph.ttl", format="turtle")
    print(f" - test/{dataset}_graph.json")
    datagraph.serialize(f"{ROOT_DIR}/test/{dataset}_graph.json", format="json-ld", auto_compact=True, indent=4)
    # Write jobmap to file
    print(f"Write jobmap to file:")
    print(f" - test/{dataset}_jobmap.ttl")
    jobmap.serialize(f"{ROOT_DIR}/test/{dataset}_jobmap.ttl", format="ttl")
    print(f" - test/{dataset}_jobmap.trig")
    jobmap.serialize(f"{ROOT_DIR}/test/{dataset}_jobmap.trig", format="trig")
    print(f" - test/{dataset}_jobmap.json")
    jobmap.serialize(f"{ROOT_DIR}/test/{dataset}_jobmap.json", format="json-ld", auto_compact=True, indent=4)
    print(f" - test/{dataset}_jobmap_framed.json")
    jsonld_frame(f"{ROOT_DIR}/test/{dataset}_jobmap.json", frame=jobmap_frame)
    print(f" - test/{dataset}_jobmap_stripped.json")
    jsonld_strip(f"{ROOT_DIR}/test/{dataset}_jobmap_framed.json")
    return jobmap