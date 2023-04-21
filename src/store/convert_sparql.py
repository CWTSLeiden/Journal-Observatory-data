from functools import partial
from time import sleep
from random import uniform as random
from rdflib import Dataset, ConjunctiveGraph
from utils.pad import PADGraph
from utils.print import print_verbose
from store.convert import batch_convert, graph_to_pad, pad_add_docinfo, queries_replace


def sparql_platform_list(query, limit=None, offset=None):
    limit_str = f"LIMIT {limit}" if limit else ""
    offset_str = f"OFFSET {offset}" if offset else ""
    query = f"{query} {limit_str} {offset_str}"

    g = PADGraph()
    print_verbose("Querying journal list...", flush=True)
    query_result = g.query(query)
    platforms = [item.get('platform') for item in query_result]
    print_verbose(f"Process {len(platforms)} journals")
    return platforms


def sparql_journal_to_pad(graph: ConjunctiveGraph, journal : str, queries : list):
    journal_queries = queries_replace(queries, {"journal_id": journal})
    return graph_to_pad(graph, journal_queries)
        

def sparql_record_to_pad(record : str, queries : list, docinfo={}):
    # Don't overload the sparql-endpoint
    sleep(random(0,1))
    pad = PADGraph()
    pad = sparql_journal_to_pad(pad, record, queries)
    pad = pad_add_docinfo(pad, docinfo)
    return pad


def sparql_journal_convert(db : Dataset, journals : list, queries : list, sparql_endpoint, batchsize, docinfo={}, processes=None):
    queries = queries_replace(queries, {"sparql_endpoint": sparql_endpoint})
    record_to_pad = partial(sparql_record_to_pad, queries=queries, docinfo=docinfo)
    batch_convert(db, journals, record_to_pad, batchsize=batchsize, processes=processes)

