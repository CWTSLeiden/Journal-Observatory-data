from flask import render_template
from rdflib import URIRef
from rdflib.query import ResultRow
from utils.store import sparql_store_config
from utils.namespace import PADNamespaceManager
from utils.pad import PADGraph
from utils import job_config as config
import json


def result_to_dict(row : ResultRow):
    d = {}
    for key, index in row.labels.items():
        d[key] = row[index]
    return d


def sparql_post_process(results, nm=None):
    def process_item(item):
        item = item.n3(nm) if item else ""
        if len(item) > 0:
            if item[0] == "<" and item[-1] == ">":
                return item[1:-1]
            elif item[0] == "\"" and item[-1] == "\"":
                return item[1:-1]
            elif "^^" in item:
                item = item.split("^^")
                return f"{item[0][1:-1]} ({item[1]})"
        return item
    for k, v in results.items():
        results[k] = process_item(v)
    return results


def parse_results(results, nm=None, post_process=True):
    if not nm:
        nm = PADNamespaceManager()
    parsed = []
    for row in results:
        newrow = result_to_dict(row)
        if post_process:
            newrow = sparql_post_process(newrow, nm)
        parsed.append(newrow)
    return parsed
            


def display_pad(pad_id, db):
    pad = PADGraph(pad_id)

    metadata_query = """
        construct {
            ?b ?p ?o .
            ?b ppo:_src ?creator .
        }
        where {
            graph ?a { ?s a ppo:Platform ; ?p ?o } .
            optional { 
                graph ?g { ?s a ppo:Platform ; ?p ?o } .
                ?g dcterms:creator ?creator
            } .
            bind(bnode() as ?b)
            filter(?p in (schema:name, schema:url, ppo:hasKeyword))
        }
    """
    identifier_query = """
        construct {
            ?b ?p ?o .
            ?b ppo:_src ?creator .
        }
        where {
            graph ?a { ?s a ppo:Platform ; ?p ?o } .
            optional { 
                graph ?g { ?s a ppo:Platform ; ?p ?o } .
                ?g dcterms:creator ?creator
            } .
            {
                ?p rdfs:subPropertyOf ?type.
                filter(?type in (dcterms:identifier))
                bind(bnode() as ?b)
            }
        }
    """
    organizations_query = """
        construct {
            ?org ?p ?o .
            ?org ppo:_src ?creator .
        }
        where {
            graph ?a {
                ?platform a ppo:Platform ; ppo:hasOrganization ?org .
                ?org ?p ?o .
            } .
            optional { 
                graph ?g {
                    ?platform a ppo:Platform ; ppo:hasOrganization ?org .
                }
                ?g dcterms:creator ?creator
            } .
        }
    """
    sources_query = """
        construct { ?s ?p ?o . }
        where {
            ?a pad:hasSourcePAD ?pad .
            optional {
                service ?pad_db {
                    ?pad pad:hasProvenance ?provenance .
                    graph ?provenance { ?s ?p ?o } .
                }
            }
        }
    """
    policies_query = """
        construct {
            ?policy ppo:_src ?creator .
            ?policy ?p ?o .
            ?o ?pp ?oo .
        }
        where {
            graph ?a { 
                ?platform a ppo:Platform ; ppo:hasPolicy ?policy .
                ?policy ?p ?o .
                optional { ?o ?pp ?oo } .
            }
            optional { 
                graph ?g { ?platform a ppo:Platform ; ppo:hasPolicy ?policy . }
                ?g dcterms:creator ?creator
            } .
        }
    """

    bindings = {'a': pad.assertion_id, 'pad_db': URIRef("repository:pad") }

    def query(q):
        query_result = db.query(q, initBindings=bindings)
        serialized = query_result.serialize(format="json-ld", auto_compact=True) or ""
        return json.loads(serialized).get("@graph")

    return render_template(
        "pad_template.html",
        pad_id=pad_id,
        metadata=query(metadata_query),
        identifier=query(identifier_query),
        organizations=query(organizations_query),
        sources=query(sources_query),
        policies=query(policies_query)
    )


def test(n=0):
    job_db = sparql_store_config(config, update=True)
    q_pad_id = f"select ?pad where {{ ?pad a pad:PAD }} limit 1 offset { n }"
    pad_id = parse_results(job_db.query(q_pad_id), post_process=False)[0].get("pad")
    return display_pad(pad_id, job_db)
