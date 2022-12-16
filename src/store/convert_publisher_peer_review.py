from store.convert import convert, read_query_file
from utils.print import print_verbose
from utils.utils import job_config as config
from glob import glob
from utils.utils import file_to_json

if __name__ == "__main__":
    print_verbose("Convert dataset: publisher_peer_review")
    dataset_config = config["publisher_peer_review"]

    debug = config.getboolean("main", "debug", fallback=False)
    bulk_path = dataset_config.get("bulk_path")
    files = glob(f"{bulk_path}/data/*.json")
    context = file_to_json(dataset_config.get("context_file"))
    queries = read_query_file(dataset_config.get("convert_file"))
    limit = dataset_config.getint("limit", fallback=len(files))
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback=None)

    if debug:
        from store.test import dataset_convert_test
        item = dataset_config.getint("test_item", fallback=0)
        dataset_convert_test("publisher_peer_review", files, context, queries, item, creator_id)
    convert(files, context, queries, limit, batchsize, creator_id)
