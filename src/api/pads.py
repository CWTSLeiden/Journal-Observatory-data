from flask import abort, request
from marshmallow import ValidationError
from api.rest import ApiResource
from api.pad import PADView
from utils.query import get_results
from utils.utils import ROOT_DIR
from configparser import ConfigParser
from utils.graph import get_mapping
import json
import re


class PADsView(ApiResource):
    def __init__(self):
        super().__init__()

    def post(self):
        args = request.get_json(force=True, silent=True) or dict()
        self.set_args(args)
        return self.get_pads()
        
    def get(self):
        """
        Get a list of pads, optionally based on a filter.
        ---
        tags:
          - PADs
        parameters:
          - name: limit
            description: The maximum number of PADs to load
            in: query
            type: integer
            required: false
            default: 10
          - name: page
            description: Which page of the results to load
            in: query
            type: integer
            required: false
            default: 0
          - name: filter
            description: |
              A list of string filters.
              Each filter should be of the format `{key}:{modifier}{value}`.
              Filters are separated by a comma (,) which means 'and'.
                - `key` can be one of (`creator`, `created`, `license`)
                  prefixed with either `p_` for _provenance_ or `d_` for _docinfo_
                - `modifier` can be one of (`!`, `<`, `>`)
                  `!` means 'not', `<` and `>` are only applicable to int and date fields.

              **example**: _Get all pads created by DOAJ in 2022_
              `p_creator:<https://doaj.org>,p_created:>2022-01-01,p_created:<2022-12-31`
              
            in: query
            type: string
            required: false
        responses:
          200:
            description: A list of PADs
        produces:
          - application/json
        """
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
        args = dict((k, v) for k, v in request_args.items() if v != None)
        self.meta.update(self.schema.load(args))
        # except ValidationError as e:
        #     abort(401, e)
    
    def get_pads(self):
        if self.meta.filter:
            query, total_query = self.get_pads_filter()
        else:
            query, total_query = self.get_pads_base()
        self.get_pads_query(query, total_query)
        return self.api_return()

    def get_pads_query(self, query, total_query):
        self.check_total(total_query)
        self.check_paging()
        try:
            query_results = self.db.query(query)
            self.results = get_results(query_results)
        except Exception:
            print(query)
            abort(500, "error in query")

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



class PADsIdView(PADView):
    def get(self, id):
        """
        Get the content of a single PAD
        """
        graph = self.pad_from_id(self.db, id)
        return self.api_return(graph, "json-ld")


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
            neg = "NOT" if eq in ("!") else ""
            eq = "=" if eq in ("!", "") else eq
            filters.append(f"FILTER {neg} EXISTS {{ FILTER (?{key} {eq} {sparqlify_string(val)}) }}")
    return " ".join(filters)


def parse_filter_dict(filter_string):
    if not filter_string:
        return None
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
            filter["modifier"] = val[0]
            filter["value"] = val[1:]
        if get_mapping(filter["value"], mapping):
            filter["value"] = f"<{get_mapping(val, mapping)}>"

        if not filters.get(key):
            filters[key] = []
        filters[key].append(filter)
    return filters

