from rdflib.graph import ConjunctiveGraph
from utils.graph import pad_graph, add_graph_context
from utils.namespace import PADNamespaceManager, PAD
from flask import render_template, request, abort
from flask.views import MethodView
from flask.helpers import make_response
from utils.store import sparql_store
import json
from rdflib import ConjunctiveGraph


class PADView(MethodView):
    def __init__(self):
        self.graph = ConjunctiveGraph()
        self.db = sparql_store()

    def get(self, id):
        """
        Get the content of a single PAD
        ---
        tags: [PAD]
        parameters:
            - name: id
              description: Identifier of the PAD
              in: path
              type: string
              required: true
            - name: format
              description: The output format
              in: query
              type: string
              enum: [json,trig,html]
              required: false
              default: json
        responses:
            200: 
                description: A single pad
        produces:
            - application/json
            - text/html
        """
        graph = self.pad_from_id(id)
        format = request.args.get("format", "json-ld")
        return self.api_return(graph, format)

    def api_return(self, graph : ConjunctiveGraph, format):
        if len(graph) == 0:
            abort(404, "PAD not found")
        if format in ("ttl", "trig"):
            data = self.api_pad_trig(graph)
        elif format in ("html"):
            data = self.api_pad_graphical(graph)
        else:
            data = self.api_pad_json(graph)
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

    def pad_from_id(self, id, sub=None) -> ConjunctiveGraph:
        id = PAD[id]
        graph = pad_graph(nm=PADNamespaceManager(this=id))
        if sub:
            add_graph_context(graph, self.db.get_context(f"{id}/{sub}"))
        else:
            add_graph_context(graph, self.db.get_context(f"{id}/docinfo"))
            add_graph_context(graph, self.db.get_context(f"{id}/assertion"))
            add_graph_context(graph, self.db.get_context(f"{id}/provenance"))
        return graph

    @staticmethod
    def api_pad_graphical(graph : ConjunctiveGraph):
        def strip_prefixes(text, invert=False):
            return "\n".join(
                filter(lambda line: ("@prefix" not in line)^invert, text.split("\n"))
            )
        SUB = graph.namespace_manager.SUB
        prefix = strip_prefixes(graph.serialize(format="trig"), invert=True)
        docinfo = strip_prefixes(graph.get_context(SUB.docinfo).serialize(format="trig"))
        provenance = strip_prefixes(graph.get_context(SUB.provenance).serialize(format="trig"))
        assertion = strip_prefixes(graph.get_context(SUB.assertion).serialize(format="trig"))
        return render_template("pad.html",
                               prefix=prefix,
                               docinfo=docinfo,
                               provenance=provenance,
                               assertion=assertion)

    @staticmethod
    def api_pad_trig(graph):
        html = graph.serialize(format='trig')
        html = html.replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{html}</pre>"

    @staticmethod
    def api_pad_json(graph):
        json_ld = graph.serialize(format="json-ld", auto_compact=True)
        return json.loads(json_ld)


class PADSubView(PADView):
    def get(self, id, sub):
        """
        Get the content of a single PAD
        ---
        tags: [PAD]
        parameters:
            - name: id
              description: Identifier of the PAD
              in: path
              type: string
              required: true
            - name: sub
              description: Subgraph of the PAD
              in: path
              type: string
              enum: [provenance,docinfo,assertion]
              required: true
              default: assertion
            - name: format
              description: The output format
              in: query
              type: string
              enum: [json,trig,html]
              required: false
              default: json
        responses:
            200: 
                description: A subgraph of a PAD
        produces:
            - application/json
            - text/html
        """
        graph = self.pad_from_id(id, sub)
        format = request.args.get("format", "json-ld")
        return self.api_return(graph, format)
