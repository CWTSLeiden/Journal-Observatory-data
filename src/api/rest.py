from flask.helpers import make_response
from api.application import api
from flask_restful import Resource, abort
from utils.query import debug_urls, get_single_result
from utils.store import sparql_store
from marshmallow import Schema, fields, INCLUDE

class ResultsMeta():
    def __init__(self, total=0, limit=None, page=None, filter=None, search=None):
        self.total = total
        self.limit = limit
        self.page = page
        self.filter = filter
        self.search = search

    def __iter__(self):
        for key in self.__dict__:
            val = getattr(self, key)
            if val:
                yield key, getattr(self, key)

    def update(self, args : dict):
        if args.get("total"): self.total = int(args.get("total", 0))
        if args.get("limit"): self.limit = int(args.get("limit", 0))
        if args.get("page"): self.page = int(args.get("page", 0))
        if args.get("filter"): self.filter = args.get("filter")
        if args.get("search"): self.search = args.get("search")
        

class MetaSchema(Schema):
    class Meta:
        unknown = INCLUDE
    class FilterSchema(Schema):
        class FilterSubSchema(Schema):
            value = fields.Str(required=True)
            modifier = fields.Str(required=False)
        p_creator = fields.List(fields.Nested(FilterSubSchema), required=False)
        p_created = fields.List(fields.Nested(FilterSubSchema), required=False)
        p_license = fields.List(fields.Nested(FilterSubSchema), required=False)
        d_creator = fields.List(fields.Nested(FilterSubSchema), required=False)
        d_created = fields.List(fields.Nested(FilterSubSchema), required=False)
        d_license = fields.List(fields.Nested(FilterSubSchema), required=False)
    filter = fields.Nested(FilterSchema, required=False)
    search = fields.Str(required=False)
    limit = fields.Int(required=False, dump_default=10)
    page = fields.Int(required=False, dump_default=0)


class ApiResource(Resource):
    def __init__(self):
        self.results = []
        self.meta = ResultsMeta()
        self.schema = MetaSchema()
        self.db = sparql_store()

    def check_limit(self):
        if self.meta.limit:
            global_limit = int(api.config.get("global_limit", 0))
            if self.meta.limit > global_limit:
                abort(400, message=f"limit exeeds global limit of {global_limit}", code=400)

    def check_paging(self):
        if self.meta.limit and self.meta.page:
            if (self.meta.limit * self.meta.page) > self.meta.total:
                abort(400, message="paging exeeds data", code=400)

    def check_total(self, total_query):
        try:
            query_result = self.db.query(total_query)
            total = get_single_result(query_result)
            if not total:
                total = 0
            self.meta.total = int(total)
        except ValueError:
            print(total_query)
            abort(400, message="error in query", code=400)

    def query_limit_offset(self):
        limit_offset = ""
        if self.meta.limit:
            limit_offset += f"limit {self.meta.limit}"
            if self.meta.page:
                limit_offset += f"limit offset {self.meta.page * self.meta.limit}"
        return limit_offset

    def api_return(self):
        data = {"meta": dict(self.meta), "results": self.results}
        if api.config.get("DEBUG"):
            data = debug_urls(data, api.config.get("host", "http://localhost:5000"))
        return make_response(data, 200, {'Content-Type': 'application/json'})

