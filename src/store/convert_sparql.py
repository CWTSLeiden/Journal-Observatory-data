from rdflib import Graph, Dataset
from utils.pad import PADGraph
from utils.print import print_verbose
from store.convert import batch_convert, graph_to_pad, pad_add_docinfo, queries_replace


def sparql_platform_list(query, limit=None, offset=None):
    limit_str = f"LIMIT {limit}" if limit else ""
    offset_str = f"OFFSET {offset}" if offset else ""
    query = f"{query} {limit_str} {offset_str}"

    g = PADGraph()
    print_verbose("Querying journal list...", end="", flush=True)
    query_result = g.query(query)
    print_verbose("Done!")
    return [item.get('platform') for item in query_result]


def sparql_journal_to_pad(journal : str, queries : list):
    journal_queries = queries_replace(queries, {"journal_id": journal})
    return graph_to_pad(PADGraph(), journal_queries)
        

def sparql_journal_convert(db : Dataset, journals : list, queries : list, sparql_endpoint, batchsize, docinfo={}):
    queries = queries_replace(queries, {"sparql_endpoint": sparql_endpoint})
    def record_to_pad(record : str):
        pad = sparql_journal_to_pad(record, queries)
        pad = pad_add_docinfo(pad, docinfo)
        return pad
    batch_convert(db, journals, record_to_pad, batchsize=batchsize)

