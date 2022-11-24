from api import api
from flask import jsonify, request, make_response
from utils.graph import job_graph
from utils.namespace import JobNamespace, PAD
from utils.store import sparql_store
import json
from configparser import ConfigParser
from utils.utils import ROOT_DIR


config = ConfigParser()
config.read(f"{ROOT_DIR}/config/api.conf")
global_limit = config.getint("main", "global_limit")


def sanitize_output_graph(graph):
    format = request.args.get("format", "json-ld")
    if format in ("ttl", "trig"):
        print(graph.namespace_manager.namespace_bindings().get("sub"))
        html = graph.serialize(format='trig')
        html = html.replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{html}</pre>"
    return jsonify(json.loads(graph.serialize(format="json-ld", auto_compact="true")))


def sanitize_output_list(query_result):
    results = []
    for r in query_result:
        if len(r) == 1: r = r[0]
        results.append(r)
    return results


def get_single_result(result_list):
    for result in result_list:
        if len(result) > 0:
            return result[0]
    return None


@api.route("/pad/<id>", methods=["GET"])
@api.route("/pad/<id>/<sub>", methods=["GET"])
def get_pad(id, sub=None):
    print(id, sub)
    db = sparql_store()
    id = PAD[id]
    graph = job_graph(nm=JobNamespace(this=id))
    if sub:
        graph.store.add_graph(db.get_context(f"{id}/{sub}"))
    else:
        graph.store.add_graph(db.get_context(f"{id}/head"))
        graph.store.add_graph(db.get_context(f"{id}/provenance"))
        graph.store.add_graph(db.get_context(f"{id}/assertion"))
        graph.store.add_graph(db.get_context(f"{id}/docinfo"))
    return sanitize_output_graph(graph)


@api.route("/api/pads")
def get_pads():
    limit = int(request.args.get("limit", 10))
    page = int(request.args.get("page", 0))
    db = sparql_store()
    total_query = "select (count(*) as ?count) where {?pad a ppo:PAD}"
    total = int(get_single_result(db.query(total_query)) or 0)
    query = f"""
        select ?pad
        where {{ ?pad a ppo:PAD }}
        limit {limit}
        offset {page * limit}
    """
    result = {"meta": {"total": total, "limit": limit, "page": page}, "results": []}
    if limit > global_limit:
        result["error"] = f"limit exeeds global limit of {global_limit}"
        return make_response(jsonify(result), 400)
    if (limit * page) > total:
        result["error"] = "paging exeeds data"
        return make_response(jsonify(result), 400)
    result["results"] = sanitize_output_list(db.query(query))
    return jsonify(result)
