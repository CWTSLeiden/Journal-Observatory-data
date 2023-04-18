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

def convert_sherpa_romeo(db : Dataset, debug=False, clear=False):
    if clear and not debug:
        print_verbose("Clear dataset: sherpa romeo")
        clear_by_creator(db, "https://v2.sherpa.ac.uk/romeo")
    print_verbose("Convert dataset: sherpa_romeo")
    dataset_config = config["sherpa_romeo"]

    data_path = dataset_config.getpath("data_path", fallback="data/sherpa_romeo")
    files = glob(f"{data_path}/data/*.json")
    context = file_to_json(dataset_config.getpath("context_file", fallback="resources/sherpa_romeo_context.json"))
    queries = read_query_file(dataset_config.getpath("convert_file", fallback="resources/sherpa_romeo_convert.sparql"))
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
        return dataset_convert_test("sherpa_romeo", files, context, queries, item, docinfo)
    json_files_convert(db, files, context, queries, batchsize, docinfo, name="Sherpa Romeo")
    return True

if __name__ == "__main__":
    from utils.store import sparql_store_config
    debug = config.getboolean("main", "debug", fallback=False)
    job_db = sparql_store_config(config, update=True)
    convert_sherpa_romeo(job_db, debug=debug, clear=True)
