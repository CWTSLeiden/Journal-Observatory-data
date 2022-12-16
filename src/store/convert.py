from utils.namespace import PADNamespaceManager, PAD
from pyld import jsonld
from pyparsing.exceptions import ParseException
from rdflib import DCTERMS, URIRef, Literal, XSD
from tqdm import tqdm as progress
from utils.graph import pad_graph
from utils.store import sparql_store
from utils.utils import file_to_json
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


def pad_add_creation_docinfo(pad, creator_id=None):
    date = datetime.date.today()
    THIS = pad.namespace_manager.THIS[""]
    SUB = pad.namespace_manager.SUB
    if creator_id:
        pad.add((THIS, DCTERMS.creator, URIRef(creator_id), SUB.docinfo))
    pad.add((THIS, DCTERMS.created, Literal(date ,datatype=XSD.date), SUB.docinfo))
    pad.add((THIS, PAD.hasDocInfo, SUB.docinfo, SUB.docinfo))
    return pad
        

def convert(files, context, queries, limit=None, batchsize=100, creator_id=None):
    sparqlstore = sparql_store(update=True)
    if not limit: limit = len(files)
    if batchsize > limit: batchsize = limit
    for n in progress(range(0, limit, batchsize), unit_scale=batchsize):
        batchgraph = pad_graph()
        for file in files[n:n+batchsize]:
            record = file_to_json(file)
            pad = json_to_pad(record, context, queries)
            pad = pad_add_creation_docinfo(pad, creator_id)
            batchgraph.addN(pad.quads())
        sparqlstore.addN(batchgraph.quads())
