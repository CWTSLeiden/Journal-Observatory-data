from utils.utils import file_to_json, ROOT_DIR
import json
from store.convert import graph_to_pad, pad_add_creation_docinfo
from store.convert_json import json_to_graph

def dataset_convert_test(dataset, files, context, queries, item, creator_id):
    record = file_to_json(files[item])
    datagraph = json_to_graph(record, context)
    pad = graph_to_pad(json_to_graph(record, context), queries)
    pad = pad_add_creation_docinfo(pad, creator_id)
    dataset_convert_test_write(dataset, record, datagraph, pad)
    return pad


def dataset_convert_test_write(dataset, record=None, datagraph=None, pad=None):
    if record:
        # Write record to file
        print(f"Write record to file:")
        print(f" - test/{dataset}_record.json")
        with open(f"{ROOT_DIR}/test/{dataset}_record.json", "w") as f:
            json.dump(record, f, indent=4)
    if datagraph:
        # Write converted graph to file
        print(f"Write data graph to file:")
        print(f" - test/{dataset}_graph.ttl")
        datagraph.serialize(f"{ROOT_DIR}/test/{dataset}_graph.ttl", format="turtle")
        print(f" - test/{dataset}_graph.json")
        datagraph.serialize(f"{ROOT_DIR}/test/{dataset}_graph.json", format="json-ld", auto_compact=True, indent=4)
    if pad:
        # Write pad to file
        print(f"Write pad to file:")
        print(f" - test/{dataset}_pad.ttl")
        pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.ttl", format="ttl")
        print(f" - test/{dataset}_pad.trig")
        pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.trig", format="trig")
        print(f" - test/{dataset}_pad.json")
        pad.serialize(f"{ROOT_DIR}/test/{dataset}_pad.json", format="json-ld", auto_compact=True, indent=4)
