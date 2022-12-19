from rdflib import Graph, Namespace, URIRef
from utils.namespace import PADNamespaceManager
from utils.graph import add_graph_context, pad_graph
from utils.print import print_graph, print_this
from store.convert import read_query_file, graph_to_pad
from utils.utils import job_config
from tqdm import tqdm as progress

test = job_config.getboolean("main", "test", fallback=False)
sparql_endpoint = job_config.get("wikidata", "bulk_url")
limit = job_config.getint("wikidata", "limit", fallback=None)
test_item = job_config.getint("wikidata", "test_item", fallback=0)
query_file = job_config.get("wikidata", "convert_file")

limit_str = f"LIMIT {limit}" if limit else ""
offset_str = ""
if test:
    limit_str = "LIMIT 1"
    offset_str = f"OFFSET {test_item}"

journal_query = f"""
SELECT ?journal
WHERE {{ 
    SERVICE <{sparql_endpoint}> {{
        ?journal wdt:P31 wd:Q5633421 . 
    }}
}}
{limit_str}
{offset_str}
"""

queries = read_query_file(query_file)

def wikidata_convert():
    r = []
    g = Graph(namespace_manager=PADNamespaceManager())

    print("Querying...", end="", flush=True)
    journals = g.query(journal_query)
    print("Done!")

    for journal in progress(journals):
        j = journal.get('journal')
        qs = [q.replace("replace_journal", j) for q in queries]
        padnm = PADNamespaceManager()
        padnm.bind("schema", Namespace("http://schema.org/"), replace=True)
        pad = pad_graph(nm=padnm)
        for query in qs:
            try:
                pad.update(query)
            except(Exception) as e:
                print(f"Error during parsing:\n\n{query}\n")
                raise(e)
        r.append((j, len(pad)))

    for j, n in r:
        print(f"{j}: {n}")
        


wikidata_convert()
