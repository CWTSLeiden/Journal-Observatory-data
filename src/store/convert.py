from configparser import ConfigParser
from glob import glob
from utils.namespace import PADNamespaceManager, PAD
from pyld import jsonld
from pyparsing.exceptions import ParseException
from rdflib import DCTERMS, URIRef, Literal, XSD
from tqdm import tqdm as progress
from utils.graph import pad_graph
from utils.jsonld import jsonld_frame, pad_frame, jsonld_strip
from utils.print import print_verbose
from utils.store import sparql_store
from utils.utils import file_to_json, ROOT_DIR
import datetime
import json
import re


def add_context(record, context={}):
    "Add the @context from the context file to the record"
    context_record = record.copy()
    for prefix, namespace in PADNamespaceManager().namespaces():
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
    if not graph: graph = pad_graph()
    record = jsonld.compact(record, record["@context"])
    graph.parse(data=json.dumps(record), format='json-ld')
    return graph


def json_to_graph(journal_json, context={}, graph=None, serialize=None):
    "Convert a json record to a graph."
    if not graph: graph = pad_graph()
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


def graph_to_pad(graph, queries, clean=True):
    jobnamespace = PADNamespaceManager()
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


def json_to_pad(journal_json, context, queries):
    graph = json_to_graph(journal_json, context)
    return graph_to_pad(graph, queries, clean=True)


def json_file_to_pad(file, context_file, queries_file):
    journal_json = file_to_json(file)
    context = file_to_json(context_file)
    queries = read_query_file(queries_file)
    return json_to_pad(journal_json, context, queries)


def pad_add_creation_docinfo(pad, config):
    config.read(f"{ROOT_DIR}/config/job.conf")
    identifier = config.get("main", "identifier")
    date = datetime.date.today()
    THIS = pad.namespace_manager.THIS[""]
    SUB = pad.namespace_manager.SUB
    pad.add((THIS, DCTERMS.creator, URIRef(identifier), SUB.docinfo))
    pad.add((THIS, DCTERMS.created, Literal(date ,datatype=XSD.date), SUB.docinfo))
    pad.add((THIS, PAD.hasDocInfo, SUB.docinfo, SUB.docinfo))
    return pad
        

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
        batchgraph = pad_graph()
        for file in files[n:n+batchsize]:
            record = file_to_json(file)
            pad = json_to_pad(record, context, queries)
            pad = pad_add_creation_docinfo(pad, config)
            batchgraph.addN(pad.quads())
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
    pad = json_to_pad(record, context, queries)
    pad = pad_add_creation_docinfo(pad, config)
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
    # Write pad to file
    print(f"Write pad to file:")
    print(f" - test/{dataset}_pad.ttl")
    pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.ttl", format="ttl")
    print(f" - test/{dataset}_pad.trig")
    pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.trig", format="trig")
    print(f" - test/{dataset}_pad.json")
    pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.json", format="json-ld", auto_compact=True, indent=4)
    print(f" - test/{dataset}_pad_framed.json")
    jsonld_frame(f"{ROOT_DIR}/test/{dataset}_pad.json", frame=pad_frame)
    print(f" - test/{dataset}_pad_stripped.json")
    jsonld_strip(f"{ROOT_DIR}/test/{dataset}_pad_framed.json")
    return pad
