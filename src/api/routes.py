from api import api
from flask import jsonify, request
from utils.query import debug_urls, get_results
from utils.store import sparql_store
import json
from api.query import *
from api.utils import *


@api.route("/pad/<id>")
@api.route("/pad/<id>/<sub>")
def get_pad(id, sub=None):
    db = sparql_store()
    graph = pad_from_id(db, id, sub)
    format = request.args.get("format", "json-ld")
    if format in ("ttl", "trig"):
        return api_pad_trig(graph)
    if format in ("graph"):
        return api_pad_graphical(graph)
    return api_pad_json(graph)


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
    result, code = api_error_global_limit(result)
    result, code = api_error_paging(result, code)
    if code == 200: result["results"] = get_results(db.query(query))
    return jsonify(debug_urls(result)), code