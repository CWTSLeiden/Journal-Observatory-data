from flask_restful import abort, request
from api.rest import ApiResource
from utils.query import get_results
from utils.utils import ROOT_DIR
from configparser import ConfigParser
from utils.graph import get_mapping
import json
import re


class PADsResource(ApiResource):
    def __init__(self):
        super().__init__()

    def post(self):
        args = request.get_json(force=True, silent=True) or dict()
        self.set_args(args)
        return self.get_pads()
        
    def get(self):
        self.meta.limit = int(request.args.get("limit", 10))
        self.meta.page = int(request.args.get("page", 0))
        args = {
            "limit": request.args.get("limit"),
            "page": request.args.get("page"),
            "filter": parse_filter_dict(request.args.get("filter")),
            "search": None
        }
        self.set_args(args)
        return self.get_pads()

    def set_args(self, request_args):
        args = {}
        for key, value in request_args.items():
            if value:
                args[key] = value
        errors = self.schema.validate(args)
        if errors:
            self.abort(400, message=str(errors), code=400)
        args = dict(self.schema.dump(args))
        self.meta.update(args)
    
    def get_pads(self):
        if self.meta.filter:
            query, total_query = self.get_pads_filter()
        else:
            query, total_query = self.get_pads_base()
        self.get_pads_query(query, total_query)
        return self.api_return()

    def get_pads_query(self, query, total_query):
        self.check_limit()
        self.check_total(total_query)
        self.check_paging()
        try:
            query_results = self.db.query(query)
            self.results = get_results(query_results)
        except Exception:
            print(query)
            abort(400, message="error in query", code=400)

    def get_pads_base(self):
        total_query = "select (count(*) as ?count) where {?pad a ppo:PAD}"
        query = f"""
            select ?pad
            where {{ ?pad a ppo:PAD }}
            {self.query_limit_offset()}
        """
        return query, total_query

    def get_pads_filter(self):
        query_filter = parse_filter_sparql(self.meta.filter)
        base_query = f"""
            ?pad a ppo:PAD ;
                ppo:hasAssertion ?assertion ;
                dcterms:creator ?d_creator ;
                dcterms:created ?d_created ;
                dcterms:license ?d_license .
            ?assertion
                dcterms:creator ?p_creator ;
                dcterms:created ?p_created ;
                dcterms:license ?p_license .
            {query_filter}
        """
        query = f"""
            select ?pad
            where {{{base_query}}}
            {self.query_limit_offset()}
        """
        total_query = f"select (count(*) as ?count) where {{{base_query}}}"
        return query, total_query

    def get_pads_search(self):
        pass


def sparqlify_string(string):
    if re.match("^[0-9]+$", string):
        return string
    if re.match("^<.+>$", string):
        return string
    if re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", string):
        return f"\"{string}\"^^xsd:date"
    if re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}.+$", string):
        return f"\"{string}\"^^xsd:dateTime"
    return f"\"{string}\""


def parse_filter_sparql(filter_dict):
    filters = []
    for key, values in filter_dict.items():
        for value in values:
            val = value.get("value")
            eq = value.get("modifier", "=")
            neg = ""
            if eq == "!":
                neg, eq = "NOT", "="
            filters.append(f"FILTER {neg} EXISTS {{ FILTER (?{key} {eq} {sparqlify_string(val)}) }}")
    return " ".join(filters)


def parse_filter_dict(filter_string):
    filters = {}
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/api.conf")
    mapping = {}
    mapping_file = config.get("main", "mapping_file")
    if mapping_file:
        with open(mapping_file) as f:
            mapping = json.load(f)
    for filter_str in filter_string.split(","):
        key, val = filter_str.split(":", 1)
        filter = {"value": val}
        if val[0] in ("!", "<", ">") and not val[-1] == ">":
            filter["mod"] = val[0]
            filter["value"] = val[1:]
        if get_mapping(filter["value"], mapping):
            filter["value"] = f"<{get_mapping(val, mapping)}>"

        if not filters.get(key):
            filters[key] = []
        filters[key].append(filter)
    return filters

