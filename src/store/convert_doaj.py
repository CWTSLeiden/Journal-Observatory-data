from store.convert import read_query_file
from store.convert_json import file_to_json, json_files_convert
from utils.print import print_verbose
from utils import job_config as config
from glob import glob

def convert_doaj(debug=False):
    print_verbose("Convert dataset: doaj")
    dataset_config = config["doaj"]

    bulk_path = dataset_config.getpath("bulk_path")
    files = glob(f"{bulk_path}/data/*.json")
    context = file_to_json(dataset_config.getpath("context_file"))
    queries = read_query_file(dataset_config.getpath("convert_file"))
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback=None)

    if limit:
        files = files[:limit]
    if debug:
        from store.test import dataset_convert_test
        item = dataset_config.getint("test_item", fallback=0)
        return dataset_convert_test("doaj", files, context, queries, item, creator_id)
    json_files_convert(files, context, queries, batchsize, creator_id)
    return True
