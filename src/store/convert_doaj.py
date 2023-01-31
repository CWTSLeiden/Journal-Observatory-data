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

def convert_doaj(db : Dataset, debug=False):
    print_verbose("Convert dataset: doaj")
    dataset_config = config["doaj"]

    data_path = dataset_config.getpath("data_path", "data/doaj")
    files = glob(f"{data_path}/data/*.json")
    context = file_to_json(dataset_config.getpath("context_file", fallback="resources/doaj_context.json"))
    queries = read_query_file(dataset_config.getpath("convert_file", fallback="resources/doaj_convert.sparql"))
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback="")

    if len(files) == 0:
        raise ValueError(f"No json records found at {data_path}/data/")
    if limit:
        files = files[:limit]
    if debug:
        from store.test import dataset_convert_test
        item = dataset_config.getint("test_item", fallback=0)
        return dataset_convert_test("doaj", files, context, queries, item, creator_id)
    json_files_convert(db, files, context, queries, batchsize, creator_id)
    return True

if __name__ == "__main__":
    from utils.store import sparql_store_config
    convert_doaj(sparql_store_config(config, update=True))
