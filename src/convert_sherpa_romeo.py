from rdflib import URIRef
from utils.graph import init_graph
from glob import glob
from convert import *
from tqdm import tqdm as progress

if __name__ == "__main__":
    from configparser import ConfigParser
    from utils.utils import ROOT_DIR

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    context_file = config.get("sherpa_romeo", "context_file")
    convert_file = config.get("sherpa_romeo", "convert_file")
    bulk_path = config.get("sherpa_romeo", "bulk_path")
    db_type = config.get("job", "db_type")
    db_path = config.get("job", "db_path")

    context = file_to_json(context_file)
    queries = read_query_file(convert_file)

    files = glob(f"{bulk_path}/data/*.json")

    # graph_id = URIRef("https://job.org/jobmap/sherpa_romeo")
    # jobmap_graph = init_graph(db_type, db_path, id=graph_id)
    # jobmap_graph.create_graph()
    # jobmap_graph.clear()

    # batchsize = 100
    # for n in progress(range(0, len(files), batchsize), unit_scale=batchsize):
    #     jobmap = init_graph()
    #     for file in files[n:n+batchsize]:
    #         sherpa_romeo_record = file_to_json(file)
    #         jobmap += json_to_jobmap(sherpa_romeo_record, context, queries)
    #     jobmap_graph.insert_graph(jobmap)

    jobmap = init_graph()
    sherpa_romeo_record = file_to_json(files[0])
    jobmap = json_to_jobmap(sherpa_romeo_record, context, queries)
    jobmap.serialize("jobmap.ttl", format="turtle")
    # jobmap_graph.serialize("jobmap.json", format="json-ld", auto_compact=True)
