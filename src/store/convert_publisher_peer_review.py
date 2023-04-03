if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from glob import glob
from rdflib import Dataset
from store.convert import read_query_file
from store.convert_json import file_to_json, json_files_convert
from utils import pad_config as config
from utils.print import print_verbose
from utils.store import clear_by_creator

def convert_publisher_peer_review(db : Dataset, debug=False, clear=False):
    if clear:
        print_verbose("Clear dataset: wikidata")
        clear_by_creator(db, "https://www.ieee.org")
        clear_by_creator(db, "https://springernature.com")
        clear_by_creator(db, "https://wiley.com")
        clear_by_creator(db, "https://elifesciences.org")
        
    print_verbose("Convert dataset: publisher_peer_review")
    dataset_config = config["publisher_peer_review"]

    data_path = dataset_config.getpath("data_path", fallback="data/publisher_peer_review")
    files = glob(f"{data_path}/data/*.json")
    context = file_to_json(dataset_config.getpath("context_file", fallback="resources/publisher_peer_review_context.json"))
    queries = read_query_file(dataset_config.getpath("convert_file", fallback="resources/publisher_peer_review_convert.sparql"))
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback="")
    sourcecode_id = config.get("main", "sourcecode", fallback="")
    docinfo = {"creator": creator_id, "sourcecode": sourcecode_id}

    if len(files) == 0:
        raise ValueError(f"No json records found at {data_path}/data/")
    if limit:
        files = files[:limit]
    if debug:
        from store.test import dataset_convert_test
        item = dataset_config.getint("test_item", fallback=0)
        return dataset_convert_test("publisher_peer_review", files, context, queries, item, docinfo)
    json_files_convert(db, files, context, queries, batchsize, docinfo, "Publishers")
    return True


if __name__ == "__main__":
    from utils.store import sparql_store_config
    debug = config.getboolean("main", "debug", fallback=False)
    job_db = sparql_store_config(config, update=True)
    convert_publisher_peer_review(job_db, debug=debug, clear=True)
