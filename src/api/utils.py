from rdflib.graph import ConjunctiveGraph
from flask import render_template, request, jsonify
from api import api
import json


def strip_prefixes(serialized, invert=False):
    result = []
    for line in serialized.split("\n"):
        if invert and "@prefix" in line:
            result.append(line)
        if not invert and not "@prefix" in line:
            result.append(line)
    return "\n".join(result)


def api_pad_graphical(graph : ConjunctiveGraph):
    SUB = graph.namespace_manager.SUB
    prefix = strip_prefixes(graph.serialize(format="trig"), invert=True)
    head = strip_prefixes(graph.get_context(SUB.head).serialize())
    docinfo = strip_prefixes(graph.get_context(SUB.docinfo).serialize())
    provenance = strip_prefixes(graph.get_context(SUB.provenance).serialize())
    assertion = strip_prefixes(graph.get_context(SUB.assertion).serialize())
    return render_template("pad.html",
                           prefix=prefix,
                           head=head,
                           docinfo=docinfo,
                           provenance=provenance,
                           assertion=assertion)


def api_pad_trig(graph):
    html = graph.serialize(format='trig')
    html = html.replace("<", "&lt;").replace(">", "&gt;")
    return f"<pre>{html}</pre>"

def api_pad_json(graph):
    return jsonify(json.loads(graph.serialize(format="json-ld", auto_compact="true")))


def api_error_global_limit(result, code=200):
    if code != 200: return result, code
    global_limit = int(api.config.get("global_limit") or 0)
    meta = result["meta"]
    if meta["limit"] > global_limit:
        code = 400
        result["error"] = {
            "code": code,
            "message": f"limit exeeds global limit of {global_limit}"
        }
    return result, code


def api_error_paging(result, code=200):
    if code != 200: return result, code
    meta = result["meta"]
    if (meta["limit"] * meta["page"]) > meta["total"]:
        code = 400
        result["error"] = {
            "code": code,
            "message": "paging exeeds data"
        }
    return result, code
