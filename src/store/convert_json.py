from store.convert import graph_to_pad, batch_convert
from utils.namespace import PADNamespaceManager
from pyld import jsonld
from utils.graph import pad_graph
import json


def file_to_json(file):
    with open(file, "rb") as f:
        return json.load(f)


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


def json_files_convert(files, context, queries, limit=None, batchsize=100, creator_id=None):
    def file_to_pad(record : str):
        graph = json_to_graph(file_to_json(record), context)
        return graph_to_pad(graph, queries, clean=True)
    batch_convert(files, file_to_pad, limit, batchsize, creator_id)
