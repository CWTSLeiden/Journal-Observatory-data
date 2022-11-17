from copy import deepcopy
from pyld import jsonld
from tqdm import tqdm as progress
import json
import os
from utils.utils import file_to_json
from utils.graph import job_graph
from namespace import JobNamespace


def issn_from_bulk(issn, data_dir):
    "Load a record from the bulk by ISSN"
    file = f"{data_dir}/{issn}.json"
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    else:
        print("Issn does not exist in files")


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


def json_file_to_graph(file, context={}, graph=None, serialize=None):
    "Convert a json file to a graph."
    if not graph: graph = job_graph()
    journal_json = file_to_json(file)
    return json_to_graph(journal_json, context, graph, serialize)


def bulk_to_graph(files, context_file, graph=None, max=None):
    """
    Convert a list of json files into a single graph
    parameters:
        files       : list of json files
        graph       : add records to an existing graph
        max         : convert a maximum number of files
        serialize   : location to store graph as file
    """
    if not graph: graph = job_graph()
    context = file_to_json(context_file)
    if context.get("@context"):
        context = context.get("@context")
    max = min(max or (2**32), len(files))
    for n, file in progress(enumerate(files), total=max):
        if n >= max: break
        graph += json_file_to_graph(file, context, graph)
    return graph


def bulk_to_rdf(files, destination, context_file, graph=None, max=(2**32), ext="ttl"):
    """
    Convert a list of json files into separate serialized files:
    parameters:
        files       : list of json files
        graph       : graph to use as template
        destination : directory to store serialized files
        max         : convert a maximum number of files
        ext         : extension for the serialized files
    """
    if not graph: graph = job_graph()
    context = file_to_json(context_file)
    if context.get("@context"):
        context = context.get("@context")
    max = min(max or (2**32), len(files))
    for n, file in progress(enumerate(files), total=max):
        if n >= max: break
        new_graph = deepcopy(graph)
        graph_file_name = os.path.basename(file).replace("json", ext)
        graph_file = os.path.join(destination, graph_file_name)
        json_file_to_graph(file, context, graph=new_graph, serialize=graph_file)
    return destination

