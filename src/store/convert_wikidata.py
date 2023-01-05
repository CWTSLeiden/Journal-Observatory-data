if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.print import print_verbose
from store.convert import read_query_file, queries_replace
from store.convert_sparql import sparql_journal_convert, sparql_journal_to_pad, sparql_platform_list
from utils import job_config as config


def wikidata_journal_list(sparql_endpoint, limit=None, offset=None):
    journal_query = f"""
        select ?platform
        where {{ 
            service <{sparql_endpoint}> {{
                ?platform wdt:P31 wd:Q5633421 . 
            }}
        }}
    """
    return sparql_platform_list(journal_query, limit, offset)


def convert_wikidata(debug=False):
    print_verbose("Convert dataset: wikidata")
    dataset_config = config["wikidata"]

    sparql_endpoint = dataset_config.get("data_location", fallback="https://query.wikidata.org/bigdata/namespace/wdq/sparql")
    limit = dataset_config.getint("limit", fallback=None)
    queries = read_query_file(dataset_config.getpath("convert_file", fallback="resources/wikidata_convert.sparql"))
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback="")

    if debug:
        from store.test import dataset_convert_test_write
        item = dataset_config.getint("test_item", fallback=0)
        journal = wikidata_journal_list(sparql_endpoint, limit=1, offset=item)[0]
        queries = queries_replace(queries, {"sparql_endpoint": sparql_endpoint})
        if journal:
            pad = sparql_journal_to_pad(journal, queries)
            dataset_convert_test_write("wikidata", pad=pad)
            return pad
        return False
    journals = wikidata_journal_list(sparql_endpoint, limit=limit)
    if len(journals) == 0:
        raise ValueError(f"No journal records found at {sparql_endpoint}")
    sparql_journal_convert(journals, queries, sparql_endpoint, batchsize, creator_id)


if __name__ == "__main__":
    convert_wikidata()
