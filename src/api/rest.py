from flask.helpers import make_response
from flask import abort
from flask.views import MethodView
from utils.query import debug_urls, get_single_result
from utils.store import sparql_store
from marshmallow import Schema, ValidationError, fields, EXCLUDE, post_load, validates, validate

class ResultsMeta():
    """
    Object that determines the meta-data of the API results.
    """
    def __init__(self, total=0, limit=10, page=0, filter=[]):
        self.total = total
        self.limit = limit
        self.page = page
        self.filter = filter

    def __iter__(self):
        for key in self.__dict__:
            val = getattr(self, key)
            if val:
                yield key, getattr(self, key)

    def update(self, meta : 'ResultsMeta'):
        for key in meta.__dict__:
            val = getattr(meta, key)
            if not val == None: setattr(self, key, val)
        

class MetaSchema(Schema):
    """
    Schema providing conversion between a meta json-object and a
    ResultsMeta object. Includes validation of json input.
    """
    class Meta:
        unknown = EXCLUDE
    class FilterSchema(Schema):
        key = fields.Str(
            required=True,
            validate=validate.OneOf([
               "a_creator",
               "a_created",
               "a_license",
               "p_identifier",
               "p_name",
               "p_organization_name"
            ])
        )
        value = fields.Str(required=True)
        modifier = fields.Str(
            required=False,
            validate=validate.OneOf(["", "!", "<", ">", "=", "~"])
        )
        @validates("value")
        def validate_value(self, value):
            if any(string in value for string in ("\"", "\'")):
                raise ValidationError(f"Modifier contains invalid value: {value}")

    filter = fields.List(fields.Nested(FilterSchema), required=False)
    limit = fields.Int(required=False, dump_default=10, load_default=10)
    @validates("limit")
    def validate_limit(self, value):
        from api.application import api
        global_limit = int(api.config.get("global_limit", 0))
        if value > global_limit:
            raise ValidationError(f"limit of {value} exeeds global limit of {global_limit}")
    page = fields.Int(required=False, dump_default=0, load_default=0)

    @post_load
    def make_meta(self, data, **kwargs) -> ResultsMeta:
        "schema.load provides a ResultsMeta object"
        return ResultsMeta(**data)


class ApiResource(MethodView):
    def __init__(self):
        self.results = []
        self.meta = ResultsMeta()
        self.schema = MetaSchema()
        self.db = sparql_store()

    def check_paging(self):
        """
        Throw an error if the paging exeeds the data.
        To prevent excessive querying by automated API calls.
        """
        if self.meta.limit and self.meta.page:
            if (self.meta.limit * self.meta.page) > 1000000:
                abort(404, "paging exeeds data")
            if self.meta.total:
                if (self.meta.limit * self.meta.page) > self.meta.total:
                    abort(404, "paging exeeds data")

    def check_total(self, total_query):
        """
        Set the total number of PADs that the query can return.
        To prevent excessive querying by automated API calls, paging is checked
        twice, once before the database query, once after.
        """
        self.check_paging()
        try:
            query_result = self.db.query(total_query)
            total = get_single_result(query_result)
            if not total:
                total = 0
            self.meta.total = int(total)
            self.check_paging()
        except ValueError:
            print(total_query)
            abort(500, "error in query")

    def query_limit_offset(self):
        """
        Construct the LIMIT and OFFSET syntax of the SPARQL query based on the
        paging of the api call.
        """
        limit_offset = ""
        if self.meta.limit:
            limit_offset += f"limit {self.meta.limit}"
            if self.meta.page:
                limit_offset += f" offset {self.meta.page * self.meta.limit}"
        return limit_offset

    def api_return(self):
        """
        Construct the api response based on the properties of the api call.
        """
        data = {"meta": dict(self.meta), "results": self.results}
        from api.application import api
        if api.config.get("DEBUG"):
            data = debug_urls(data, api.config.get("host", "http://localhost:5000"))
        return make_response(data, 200, {'Content-Type': 'application/json'})

