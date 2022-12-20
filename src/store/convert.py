from utils.namespace import PADNamespaceManager, PAD
from pyparsing.exceptions import ParseException
from rdflib import DCTERMS, URIRef, Literal, XSD
from tqdm import tqdm as progress
from utils.graph import pad_graph
from utils.store import sparql_store
import datetime
import re


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


def pad_add_creation_docinfo(pad, creator_id=None):
    date = datetime.date.today()
    THIS = pad.namespace_manager.THIS[""]
    SUB = pad.namespace_manager.SUB
    if creator_id:
        pad.add((THIS, DCTERMS.creator, URIRef(creator_id), SUB.docinfo))
    pad.add((THIS, DCTERMS.created, Literal(date ,datatype=XSD.date), SUB.docinfo))
    pad.add((THIS, PAD.hasDocInfo, SUB.docinfo, SUB.docinfo))
    return pad
        

def batch_convert(records, record_to_pad, limit=None, batchsize=100, creator_id=None):
    sparqlstore = sparql_store(update=True)
    if not limit: limit = len(records)
    if batchsize > limit: batchsize = limit
    for n in progress(range(0, limit, batchsize), unit_scale=batchsize):
        batchgraph = pad_graph()
        for record in records[n:n+batchsize]:
            pad = record_to_pad(record)
            if creator_id:
                pad = pad_add_creation_docinfo(pad, creator_id)
            batchgraph.addN(pad.quads())
        sparqlstore.addN(batchgraph.quads())
