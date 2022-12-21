from store.convert import read_query_file
from store.convert_json import file_to_json, json_files_convert
from utils.print import print_verbose
from utils import job_config as config
from glob import glob

def convert_sherpa_romeo(debug=False):
    print_verbose("Convert dataset: sherpa_romeo")
    dataset_config = config["sherpa_romeo"]

    data_path = dataset_config.getpath("data_path", fallback="data/sherpa_romeo")
    files = glob(f"{data_path}/data/*.json")
    context = file_to_json(dataset_config.getpath("context_file", fallback="resources/sherpa_romeo_context.json"))
    queries = read_query_file(dataset_config.getpath("convert_file", fallback="resources/sherpa_romeo_convert.sparql))
    limit = dataset_config.getint("limit", fallback=None)
    batchsize = dataset_config.getint("batchsize", fallback=100)
    creator_id = config.get("main", "identifier", fallback=None)

    if limit:
        files = files[:limit]
    if debug:
        from store.test import dataset_convert_test
        item = dataset_config.getint("test_item", fallback=0)
        return dataset_convert_test("sherpa_romeo", files, context, queries, item, creator_id)
    json_files_convert(files, context, queries, batchsize, creator_id)
    return True
