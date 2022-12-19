from rdflib import Graph, URIRef

g = Graph(store="SPARQLStore")

# https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format#Full_list_of_prefixes
wikidata_prefixes = {
    "bd": URIRef("http://www.bigdata.com/rdf#"),
    "cc": URIRef("http://creativecommons.org/ns#"),
    "dct": URIRef("http://purl.org/dc/terms/"),
    "geo": URIRef("http://www.opengis.net/ont/geosparql#"),
    "hint": URIRef("http://www.bigdata.com/queryHints#"), 
    "ontolex": URIRef("http://www.w3.org/ns/lemon/ontolex#"),
    "owl": URIRef("http://www.w3.org/2002/07/owl#"),
    "prov": URIRef("http://www.w3.org/ns/prov#"),
    "rdf": URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    "rdfs": URIRef("http://www.w3.org/2000/01/rdf-schema#"),
    "schema": URIRef("http://schema.org/"),
    "skos": URIRef("http://www.w3.org/2004/02/skos/core#"),
    "xsd": URIRef("http://www.w3.org/2001/XMLSchema#"),
    "p": URIRef("http://www.wikidata.org/prop/"),
    "pq": URIRef("http://www.wikidata.org/prop/qualifier/"),
    "pqn": URIRef("http://www.wikidata.org/prop/qualifier/value-normalized/"),
    "pqv": URIRef("http://www.wikidata.org/prop/qualifier/value/"),
    "pr": URIRef("http://www.wikidata.org/prop/reference/"),
    "prn": URIRef("http://www.wikidata.org/prop/reference/value-normalized/"),
    "prv": URIRef("http://www.wikidata.org/prop/reference/value/"),
    "psv": URIRef("http://www.wikidata.org/prop/statement/value/"),
    "ps": URIRef("http://www.wikidata.org/prop/statement/"),
    "psn": URIRef("http://www.wikidata.org/prop/statement/value-normalized/"),
    "wd": URIRef("http://www.wikidata.org/entity/"),
    "wdata": URIRef("http://www.wikidata.org/wiki/Special:EntityData/"),
    "wdno": URIRef("http://www.wikidata.org/prop/novalue/"),
    "wdref": URIRef("http://www.wikidata.org/reference/"),
    "wds": URIRef("http://www.wikidata.org/entity/statement/"),
    "wdt": URIRef("http://www.wikidata.org/prop/direct/"),
    "wdtn": URIRef("http://www.wikidata.org/prop/direct-normalized/"),
    "wdv": URIRef("http://www.wikidata.org/value/"),
    "wikibase": URIRef("http://wikiba.se/ontology#")
}


query = """
SELECT ?journal ?iso 
WHERE {
    ?journal wdt:P31 wd:Q5633421 . # is scientific journal
    ?journal wdt:P407 ?language .  # journal has language
    ?language wdt:P218 ?iso .      # language has iso code
}
LIMIT 100
"""
print("Querying...", end="", flush=True)
g.open("http://query.wikidata.org/sparql")
results = g.query(query, initNs=wikidata_prefixes)
print("Done!")

for result in results:
    print([str(r) for r in result])
