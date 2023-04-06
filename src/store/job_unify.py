if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from functools import partial
from tqdm import tqdm as progress
from rdflib import Dataset
from rdflib.term import URIRef
from store.convert import batch_convert
from utils.graphdb import graphdb_setup
from utils.pad import PADGraph
from utils.print import print_verbose
from utils.store import sparql_store_config
from utils.namespace import PAD, RDF, PPO
from utils import ROOT_DIR, job_config, pad_config


def cluster_pairs(pad_pairs):
    pad_sets = dict()
    print_verbose("Cluster PADs")
    for pad1, pad2 in progress(pad_pairs):
        if pad_sets.get(pad1) is None:
            pad_sets[pad1] = { pad1 }
        pad_sets[pad1].add(pad2)
    clusters = []
    pad_done = set()
    print_verbose("De-duplicate PADs")
    for named_pad, pad_set in progress(pad_sets.items()):
        if named_pad not in pad_done:
            clusters.append(pad_set)
            pad_done = pad_done.union(pad_set)
    return clusters


def cluster_to_pad(db : Dataset, pad_ids : set[URIRef]):
    unipad = PADGraph()
    THIS = unipad.THIS
    SUB = unipad.SUB
    unipad.add((THIS, RDF.type, PAD.PAD, SUB.docinfo))
    unipad.add((THIS, PAD.hasAssertion, SUB.assertion, SUB.docinfo))
    unipad.add((THIS, PAD.hasProvenance, SUB.provenance, SUB.docinfo))
    unipad.add((SUB.platform, RDF.type, PPO.Platform, SUB.assertion))
    for pad_id in pad_ids:
        assertion = db.get_context(f"{pad_id}/assertion")
        unipad.add_context(assertion, SUB.assertion)
        unipad.add_context(db.get_context(f"{pad_id}/provenance"))
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
    }
    """
    result = db.query(pad_eq_query)
    pad_same_query = """
    select ?pad1 ?pad2 where
    {
        ?pad1 pad:assertsSamePlatform+ ?pad2
    }
    """
    print_verbose("Get all PADs")
    pairs = list(result.graph.query(pad_same_query))
    return cluster_pairs(pairs)


def unify_pads(source_db, target_db, batch_size=25, debug=False):
    cluster_to_pad_partial = partial(cluster_to_pad, db=source_db)
    clusters = pad_clusters(source_db)
    if debug:
        unipad = cluster_to_pad(clusters[0])
        unipad.serialize(f"{ROOT_DIR}/test/unipad.trig", format="trig")
        unipad.serialize(f"{ROOT_DIR}/test/unipad.json", format="json-ld", auto_compact=True)
    else:
        print_verbose("Store PADs")
        batch_convert(target_db, clusters, cluster_to_pad_partial, batch_size)


if __name__ == "__main__":
    debug = job_config.getboolean("main", "debug", fallback=False)
    job_db = graphdb_setup(job_config, "job", recreate=True)
    pad_db = sparql_store_config(pad_config, update=False)
    unify_pads(pad_db, job_db, debug=debug)
