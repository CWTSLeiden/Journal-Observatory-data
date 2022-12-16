from api.pad import PADView
from api.rest import ApiResource
from flask import abort, request
from utils.query import get_results
import re


class PADsView(ApiResource):
    def __init__(self):
        super().__init__()

    def post(self):
        """
        Get a list of pads, optionally based on a filter.
        ---
        tags:
          - PADs
        parameters:
          - name: query
            in: body
            required: false
            schema:
              type: object
              properties:
                limit:
                  description: The maximum number of PADs to load
                  type: integer
                  default: 10
                  maximum: 50
                page:
                  description: Which page of the results to load, first page has index 0
                  type: integer
                  default: 0
                filter:
                  description: A list of string filters.
                  type: array
                  items:
                    type: object
                    properties:
                      key:
                        type: string
                        enum: [a_creator, a_created, a_license, p_identifier, p_name, p_organization_name]
                        description: |
                          a_creator: Creator of the assertion
                          a_created: Creation date of the assertion
                          a_license: License of the assertion
                          p_identifier: Any identifier of the platform
                          p_name: Name of the platform
                          p_organization_name: Name of any organization belonging to the platform
                      modifier:
                        type: string
                        enum: ["=", "~", "!", "<", ">"]
                        description: |
                          = means 'is'
                          ~ means 'contains'
                          ! means 'not'
                          < and > are only applicable to int and date fields.
                      value:
                        type: string
                        description: |
                          value is a string value, if it is an IRI it needs to be in angled brackets (<{value}>)
        responses:
          200:
            description: A list of PADs
        produces:
          - application/json
        """
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
                - `key` can be one of:
                  - a_creator: Creator of the assertion
                  - a_created: Creation date of the assertion
                  - a_license: License of the assertion
                  - p_identifier: Any identifier of the platform
                  - p_name: Name of the platform
                  - p_organization_name: Name of any organization belonging to the platform
                - `modifier` can be one of (`=`, `~`, `!`, `<`, `>`)
                  - = means 'is'
                  - ~ means 'contains'
                  - ! means 'not'
                  - < and > are only applicable to int and date fields.
                - `value` is a string value, if it is an IRI it needs to be in angled brackets (<{value}>)

              **example**: _Get all pads created by DOAJ in 2022_
              `a_creator:<https://doaj.org>,a_created:>2022-01-01,a_created:<2022-12-31`
              
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
            "filter": parse_filter_dict(request.args.get("filter", "")),
            "search": None
        }
        self.set_args(args)
        return self.get_pads()

    def set_args(self, request_args : dict):
        """
        Update the meta object with the body of the request.
        """
        args = dict((k, v) for k, v in request_args.items() if v != None)
        self.meta.update(self.schema.load(args))
    
    def get_pads(self):
        """
        Construct the appropriate SPARQL queries based on the request parameters
        and return the results of those queries.
        """
        if self.meta.filter:
            query, total_query = self.get_pads_filter()
        else:
            query, total_query = self.get_pads_base()
        self.get_pads_query(query, total_query)
        return self.api_return()

    def get_pads_query(self, query, total_query):
        """
        Execute a SPARQL query after some sanity checks.
        """
        self.check_total(total_query)
        try:
            query_results = self.db.query(query)
            self.results = get_results(query_results)
        except Exception:
            print(query)  # TODO: for debugging
            abort(500, "error in query")

    def get_pads_base(self):
        """
        Construct a simple SPARQL query that returns a list of PADs without filter
        """
        total_query = "select (count(*) as ?count) where {?pad a pad:PAD}"
        query = f"""
            select ?pad
            where {{ ?pad a pad:PAD }}
            {self.query_limit_offset()}
        """
        return query, total_query

    def get_pads_filter(self):
        """
        Construct a SPARQL query that returns a list of PADs based on a list of filters.
        """
        query_filter = parse_filter_sparql(self.meta.filter)
        base_query = f"""
            ?pad a pad:PAD .
            ?pad pad:hasAssertion ?assertion .
            {"?assertion dcterms:creator ?a_creator ." if "?a_creator" in query_filter else ""}
            {"?assertion dcterms:created ?a_created ." if "?a_created" in query_filter else ""}
            {"?assertion dcterms:license ?a_license ." if "?a_license" in query_filter else ""}
            graph ?assertion {{ ?platform a ppo:Platform }}
            {"?platform dcterms:identifier ?p_identifier ." if "?p_identifier" in query_filter else ""}
            {"?platform schema:name ?p_name ." if "?p_name" in query_filter else ""}
            {"?platform ppo:hasOrganization [ schema:name ?p_organization_name ] ." if "?p_organization_name" in query_filter else ""}
            {query_filter}
        """
        query = f"""
            select ?pad
            where {{{base_query}}}
            {self.query_limit_offset()}
        """
        print(query)
        total_query = f"select (count(*) as ?count) where {{{base_query}}}"
        return query, total_query


class PADsIdView(PADView):
    def get(self, id):
        """
        Get the content of a single PAD.
        ---
        tags: [PADs]
        parameters:
            - name: id
              description: Identifier of the PAD
              in: path
              type: string
              required: true
        responses:
            200: 
                description: A single pad
        produces:
            - application/json
        """
        graph = self.pad_from_id(id)
        return self.api_return(graph, "json")


def sparqlify_string(string):
    """
    Some simple conversions between python strings and SPARQL syntax.
    """
    if re.match("^[0-9]+$", string):
        return string
    if re.match("^<.+>$", string):
        return string
    if re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", string):
        return f"\"{string}\"^^xsd:date"
    if re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}.+$", string):
        return f"\"{string}\"^^xsd:dateTime"
    return f"\"{string}\""


def parse_filter_sparql(filter_list : list[dict]) -> str:
    """
    Convert a list of filter objects into a SPARQL filter string.
    """
    sparql_filters = []
    for filter in filter_list:
        key = filter.get("key", "")
        val = filter.get("value", "")
        eq = filter.get("modifier", "=")
        if eq in ("~"):
            sparql = f"FILTER (contains(lcase(str(?{key})), lcase({sparqlify_string(val)})))"
        else:
            eq = "!=" if eq in ("!") else eq
            sparql = f"FILTER (?{key} {eq} {sparqlify_string(val)})"
        sparql_filters.append(sparql)
    return " ".join(sparql_filters)


def parse_filter_dict(filter_string : str) -> list[dict]:
    """
    Convert a filter string from a url ?filter= parameter into a list of
    filter objects.
      ?filter={key}:{modifier}{value},...
        -> [{"key": key, "modifier": modifier, "value": value}, ...]
    """
    filters = []
    if not filter_string:
        return filters
    for filter_str in filter_string.split(","):
        key, val = filter_str.split(":", 1)
        filter = {"key": key, "value": val}
        if val[0] in ("!", "<", ">", "~") and not (val[1] == "<" and val[-1] == ">"):
            filter["modifier"] = val[0]
            filter["value"] = val[1:]
        filters.append(filter)
    return filters

