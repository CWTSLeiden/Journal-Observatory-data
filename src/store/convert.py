from pyparsing.exceptions import ParseException
from rdflib import DCTERMS, Dataset, URIRef, Literal, XSD
from rdflib.graph import ConjunctiveGraph
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from typing import TypeVar, Callable
from time import sleep
import datetime
import re

from utils.namespace import PADNamespaceManager, PAD
from utils.pad import PADGraph
from utils.print import print_graph

def read_query_file(file : str) -> list[str]:
    """
    Read a query file and return a list of single queries.
    - Excludes comments
    - Splits on construct/insert/select
    """
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


def queries_replace(base_queries : list[str], replacements : dict) -> list[str]:
    """
    Support variables in queries.
    Return the queries with variables replaced.
    """
    queries = base_queries
    for key, value in replacements.items():
        queries = [q.replace(f"${key}", value) for q in queries]
    return queries


def graph_to_pad(graph : ConjunctiveGraph, queries : list[str], clean=True) -> ConjunctiveGraph:
    """
    Run the queries on the provided graph.
    When clean is True, remove all graphs that where present before running the queries.
    """
    padnamespace = PADNamespaceManager()
    graph.namespace_manager = padnamespace
    original_graphs = list(graph.contexts())
    for query in queries:
        try:
            graph.update(query)
        except(ParseException) as e:
            print(f"Error during parsing:\n\n{query}\n")  # TODO: for debugging
            raise(e)
    if clean:
        for original_graph in original_graphs:
            graph.remove_context(original_graph)
    return graph


def pad_add_docinfo(pad : ConjunctiveGraph, docinfo : dict={}) -> ConjunctiveGraph:
    """
    Add dcterms:created and dcterms:creator to a PAD
    """
    date = datetime.date.today()
    THIS = pad.namespace_manager.THIS[""]
    SUB = pad.namespace_manager.SUB
    if creator_id := docinfo.get("creator"):
        pad.add((THIS, DCTERMS.creator, URIRef(creator_id), SUB.docinfo))
    if sourcecode_id := docinfo.get("sourcecode"):
        pad.add((THIS, PAD.sourceCode, URIRef(sourcecode_id), SUB.docinfo))
    pad.add((THIS, DCTERMS.created, Literal(date ,datatype=XSD.date), SUB.docinfo))
    pad.add((THIS, PAD.hasDocInfo, SUB.docinfo, SUB.docinfo))
    return pad


R = TypeVar('R')

def batch_add(sparqlstore: Dataset, graph: ConjunctiveGraph):
    tries = 0
    maxtries = 10
    while tries <= maxtries:
        try:
            sparqlstore.addN(graph.quads())
        except Exception as e:
            if tries == maxtries:
                print_graph(graph)
                raise(e)
            print(e, flush=True)
            sleep(3)
        finally:
            tries = maxtries + 1

def batch_convert_run(records : list[R], record_to_pad : Callable[[R], ConjunctiveGraph]):
    batchgraph = PADGraph()
    for record in records:
        try:
            pad = record_to_pad(record)
            batchgraph.addN(pad.quads())
        except Exception as e:
            print(f"ERROR: parsing record: {record}", flush=True)
            print(e, flush=True)
    return batchgraph

def batch_convert(sparqlstore : Dataset, records : list[R], record_to_pad : Callable[[R], ConjunctiveGraph], batchsize=100, name=None):
    """
    Meta function to upload data to the SPARQL store.
    Because every addN call to the store is a single HTTP request,
    batching these requests leads to significant performance improvement.
    params:
    - records: list of records that contain the to-be-converted information
    - record_to_pad: a function that converts a record into a PAD
    - limit: total number of records to be converted
    - batchsize: number of pads contained in a batch
    """

    total = len(records)
    if batchsize > total: batchsize = total
    if total == 0:
        print("No records")
        return False

    # Separate records into batches
    batches = [records[n:n+batchsize] for n in range(0, total, batchsize)]
    process_batch = partial(batch_convert_run, record_to_pad=convert_func)
    progress = partial(tqdm, unit_scale=batchsize, total=len(batches))

    # Use imap_unordered to send results to SPARQL endpoint as soon as
    # results are available, disregarding order of call
    with Pool() as pool:
        for graph in progress(pool.imap_unordered(process_batch, batches)):
            batch_add(sparqlstore, graph)
            sleep(0.5)

    return True
