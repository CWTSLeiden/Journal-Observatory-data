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
    head = strip_prefixes(graph.get_context(SUB.head).serialize(format="trig"))
    docinfo = strip_prefixes(graph.get_context(SUB.docinfo).serialize(format="trig"))
    provenance = strip_prefixes(graph.get_context(SUB.provenance).serialize(format="trig"))
    assertion = strip_prefixes(graph.get_context(SUB.assertion).serialize(format="trig"))
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


def api_pad_json(graph, compact=True):
    json_ld = graph.serialize(format="json-ld", auto_compact=compact)
    return jsonify(json.loads(json_ld))


def api_results(total, limit, page):
    result = {"meta": {"total": total, "limit": limit, "page": page}, "results": []}
    result, code = api_error_global_limit(result)
    result, code = api_error_paging(result, code)
    return result, code


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


def parse_filter(filter_string):
    filters = []
    for filter_str in filter_string.split(","):
        key, val = filter_str.split(":")
        neg, eq = " ", "="
        if val[0] == "!":
            neg = "NOT"
            val = val[1:]
        elif val[0] in ("<", ">"):
            eq = val[0]
            val = val[1:]
        if key in ("d_creator", "p_creator", "d_license", "p_license"):
            filter = f"?{key} = \"{val}\""
        elif key in ("d_date", "p_date"):
            filter = f"?{key}^^xsd:dateTime {eq} \"{val}\"^^xsd:dateTime"
        else:
            filter = ""
        if filter:
            filters.append(f"FILTER {neg} EXISTS {{ FILTER ({ filter }) }}")
    return " ".join(filters)
