from rdflib import Graph
from utils.namespace import PADNamespaceManager
from utils.graph import pad_graph
from utils.print import print_verbose
from store.convert import batch_convert, graph_to_pad, read_query_file
from utils import job_config as config

def wikidata_journal_list(limit, sparql_endpoint, debug=False, test_item=0):
    limit_str = f"LIMIT {limit}" if limit else ""
    offset_str = ""
    if debug:
        limit_str = "LIMIT 1"
        offset_str = f"OFFSET {test_item}"

    journal_query = f"""
        select ?journal
        where {{ 
            service <{sparql_endpoint}> {{
                ?journal wdt:P31 wd:Q5633421 . 
            }}
        }}
        {limit_str}
        {offset_str}
    """
    g = Graph(namespace_manager=PADNamespaceManager())

    print_verbose("Querying journal list...", end="", flush=True)
    journals = g.query(journal_query)
    print_verbose("Done!")
    return [item.get('journal') for item in journals]


def queries_replace(base_queries : list, replacements : dict):
    queries = base_queries
    for key, value in replacements.items():
        queries = [q.replace(f"${key}", value) for q in queries]
    return queries


def wikidata_journal_to_pad(journal : str, queries : list):
    journal_queries = queries_replace(queries, {"journal_id": journal})
    return graph_to_pad(pad_graph(nm=PADNamespaceManager()), journal_queries)
        

def wikidata_journal_convert(journals : list, queries : list, sparql_endpoint, batchsize, creator_id=None):
    queries = queries_replace(queries, {"sparql_endpoint": sparql_endpoint})
    def record_to_pad(record : str):
        pad = wikidata_journal_to_pad(record, queries)
        return pad
    batch_convert(journals, record_to_pad, batchsize=batchsize, creator_id=creator_id)


def convert_wikidata(debug=False):
    print_verbose("Convert dataset: wikidata")
    dataset_config = config["wikidata"]

    sparql_endpoint = dataset_config.get("bulk_url")
    limit = dataset_config.getint("limit", fallback=None)
    queries = read_query_file(dataset_config.get("convert_file"))
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback=None)

    if debug:
        from store.test import dataset_convert_test_write
        item = dataset_config.getint("test_item", fallback=0)
        journal = wikidata_journal_list(limit, sparql_endpoint, debug, item)[0]
        queries = queries_replace(queries, {"sparql_endpoint": sparql_endpoint})
        pad = wikidata_journal_to_pad(journal, queries)
        dataset_convert_test_write("wikidata", pad=pad)
        return True
    journals = wikidata_journal_list(limit, sparql_endpoint)
    wikidata_journal_convert(journals, queries, sparql_endpoint, batchsize, creator_id)

if __name__ == "__main__":
    convert_wikidata()
