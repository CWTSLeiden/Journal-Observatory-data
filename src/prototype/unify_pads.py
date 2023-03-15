if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rdflib import Dataset
from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef
from store.convert import batch_convert
from utils.graphdb import graphdb_setup
from utils.pad import PADGraph
from utils.print import print_verbose
from utils.store import sparql_store_config
from utils.namespace import PAD, RDF
from utils import ROOT_DIR, job_config, pad_config


def cluster_pairs(pad_pairs):
    clusters = []
    stop = False
    def xor(p, q): return bool(p) ^ bool(q)
    def cluster_find(pad1, pad2):
        for cluster in clusters:
            if xor(pad1 in cluster, pad2 in cluster):
                cluster.update({pad1, pad2})
                return True, True
            elif pad1 in cluster and pad2 in cluster:
                return True, False
        return False, False
    while not stop:
        stop = True
        for pad1, pad2 in pad_pairs:
            found, update = cluster_find(pad1, pad2)
            if update: stop = False
            if not found: clusters.append({pad1, pad2})
    return clusters

def unify_pads(db : Dataset, pad_ids : set[URIRef], include_source=True):
    unipad = PADGraph()
    THIS = unipad.THIS
    SUB = unipad.SUB
    unipad.add((THIS, RDF.type, PAD.PAD, SUB.docinfo))
    unipad.add((THIS, PAD.hasAssertion, SUB.assertion, SUB.docinfo))
    unipad.add((THIS, PAD.hasProvenance, SUB.provenance, SUB.docinfo))
    for pad_id in pad_ids:
        assertion = db.get_context(f"{pad_id}/assertion")
        unipad.add_context(assertion, SUB.assertion)
        if include_source:
            unipad.add_context(assertion)
            unipad.add_context(db.get_context(f"{pad_id}/provenance"))
            unipad.add_context(db.get_context(f"{pad_id}/docinfo"))
        unipad.add((SUB.assertion, PAD.hasSourceAssertion, assertion.identifier, SUB.provenance))
    unipad.update("""
        delete { ?platform ?p ?o . }
        insert { graph ?g { sub:platform ?p ?o . } }
        where  { graph ?g { ?platform a ppo:Platform ; ?p ?o . } }
    """)
    return unipad


def pad_clusters(db : Dataset):
    pad_eq_query = """
    construct { ?pad1 pad:assertsSamePlatform ?pad2 } where
    {
        ?platform1 dcterms:identifier ?id .
        ?platform2 dcterms:identifier ?id .
        graph ?assertion1 { ?platform1 a ppo:Platform }
        graph ?assertion2 { ?platform2 a ppo:Platform }
        ?pad1 pad:hasAssertion ?assertion1 .
        ?pad2 pad:hasAssertion ?assertion2 .
        # filter(?pad1 != ?pad2) .
    }
    """
    result = db.query(pad_eq_query)
    pad_same_query = """
    select ?pad1 ?pad2 where
    {
        ?pad1 pad:assertsSamePlatform+ ?pad2
        # filter(?pad1 != ?pad2)
    }
    """
    pairs = list(result.graph.query(pad_same_query))
    return cluster_pairs(pairs)


def store_pads(source_db, target_db, debug=False):
    def cluster_to_pad(cluster) -> ConjunctiveGraph:
        return unify_pads(source_db, cluster, include_source=False)
    clusters = pad_clusters(source_db)
    if debug:
        unipad = cluster_to_pad(clusters[0])
        unipad.serialize(f"{ROOT_DIR}/test/unipad.trig", format="trig")
        unipad.serialize(f"{ROOT_DIR}/test/unipad.json", format="json-ld", auto_compact=True)
    else:
        print_verbose("Store unipads")
        batch_convert(target_db, clusters, cluster_to_pad, 100)


if __name__ == "__main__":
    debug = job_config.getboolean("main", "debug", fallback=False)
    job_db = graphdb_setup(job_config, "job")
    pad_db = sparql_store_config(pad_config, update=False)
    store_pads(pad_db, job_db, debug=debug)
