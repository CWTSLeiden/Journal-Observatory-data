from flask import render_template
from flask.helpers import make_response
from flask_restful import Resource, request, abort
from api.query import pad_from_id
from utils.store import sparql_store
import json
from rdflib import ConjunctiveGraph

class PADResource(Resource):
    def __init__(self):
        self.graph = ConjunctiveGraph()
        self.db = sparql_store()

    def get(self, id, sub=None):
        self.graph = pad_from_id(self.db, id, sub)
        if len(self.graph) == 0:
            abort(403, message="PAD not found", code=403)
        format = request.args.get("format", "json-ld")
        if format in ("ttl", "trig"):
            data = self.api_pad_trig()
        elif format in ("html"):
            data = self.api_pad_graphical()
        else:
            data = self.api_pad_json()
        return make_response(data, 200, self.header(format))

    @staticmethod
    def header(format="json"):
        map = {
            "json": "application/json",
            "trig": "text/html",
            "ttl": "text/html",
            "html": "text/html"
        }
        return {'Content-Type': map.get(format, "application/json")}

    def api_pad_graphical(self):
        SUB = self.graph.namespace_manager.SUB
        prefix = strip_prefixes(self.graph.serialize(format="trig"), invert=True)
        head = strip_prefixes(self.graph.get_context(SUB.head).serialize(format="trig"))
        docinfo = strip_prefixes(self.graph.get_context(SUB.docinfo).serialize(format="trig"))
        provenance = strip_prefixes(self.graph.get_context(SUB.provenance).serialize(format="trig"))
        assertion = strip_prefixes(self.graph.get_context(SUB.assertion).serialize(format="trig"))
        return render_template("pad.html",
                               prefix=prefix,
                               head=head,
                               docinfo=docinfo,
                               provenance=provenance,
                               assertion=assertion)

    def api_pad_trig(self):
        html = self.graph.serialize(format='trig')
        html = html.replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{html}</pre>"

    def api_pad_json(self):
        json_ld = self.graph.serialize(format="json-ld", auto_compact=True)
        return json.loads(json_ld)


def strip_prefixes(serialized, invert=False):
    result = []
    for line in serialized.split("\n"):
        if invert and "@prefix" in line:
            result.append(line)
        if not invert and not "@prefix" in line:
            result.append(line)
    return "\n".join(result)

