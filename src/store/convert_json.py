from rdflib.graph import ConjunctiveGraph
from store.convert import graph_to_pad, batch_convert, pad_add_creation_docinfo
from utils.namespace import PADNamespaceManager
from pyld import jsonld
from utils.graph import pad_graph
import json


def file_to_json(file : str) -> dict :
    with open(file, "rb") as f:
        return json.load(f)


def add_context(record : dict, context : dict) -> dict :
    """
    Add the @context from the context file to the record
    """
    context_record = record.copy()
    for prefix, namespace in PADNamespaceManager().namespaces():
        if not context.get(prefix):
            context[prefix] = namespace
    context_record["@context"] = context
    context_record["@type"] = "http://www.w3.org/2004/03/trix/rdfg-1/Graph"
    return context_record


def json_to_graph(record : dict, context : dict) -> ConjunctiveGraph:
    """
    Convert a json record to a graph.
    """
    graph = pad_graph()
    record = add_context(record, context)
    record = jsonld.compact(record, record["@context"])
    graph.parse(data=json.dumps(record), format='json-ld')
    return graph


def json_files_convert(files : list[str], context : dict, queries : list[str], batchsize=100, creator_id=None):
    def file_to_pad(record : str) -> ConjunctiveGraph:
        graph = json_to_graph(file_to_json(record), context)
        pad = graph_to_pad(graph, queries, clean=True)
        pad = pad_add_creation_docinfo(pad, creator_id)
        return pad
    batch_convert(files, file_to_pad, batchsize)
