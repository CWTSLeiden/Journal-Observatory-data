from rdflib import ConjunctiveGraph, Graph, Dataset
from utils.namespace import PAD_PREFIX, PADNamespaceManager, RDF, SCPO


class PADGraph(ConjunctiveGraph):
    def __init__(self, identifier=None, prefix=PAD_PREFIX):
        namespace_manager = PADNamespaceManager(this=identifier, prefix=prefix)
        self.THIS = namespace_manager.THIS[""]
        self.SUB = namespace_manager.SUB

        super().__init__(identifier=self.THIS)

        self.namespace_manager = namespace_manager
        self.provenance_id = self.SUB.provenance
        self.assertion_id = self.SUB.assertion
        self.docinfo_id = self.SUB.docinfo

    def add_context(self, context : Graph, identifier=None):
        if not identifier:
            identifier = context.identifier   
        for subj, pred, obj in context:
            self.add((subj, pred, obj, identifier))

    def build(self, db : Dataset, sub=None):
        if sub:
            self.add_context(db.get_context(sub))
        else:
            self.add_context(db.get_context(self.provenance_id))
            self.add_context(db.get_context(self.assertion_id))
            self.add_context(db.get_context(self.docinfo_id))

    @property
    def assertion(self):
        return self.get_context(self.assertion_id)

    @assertion.setter
    def assertion(self, g : Graph):
        self.remove_context(self.assertion_id)
        self.add_context(g, self.assertion_id)

    @property
    def provenance(self):
        return self.get_context(self.provenance_id)

    @provenance.setter
    def provenance(self, g : Graph):
        self.remove_context(self.provenance_id)
        self.add_context(g, self.provenance_id)

    @property
    def docinfo(self):
        return self.get_context(self.docinfo_id)

    @docinfo.setter
    def docinfo(self, g : Graph):
        self.remove_context(self.docinfo_id)
        self.add_context(g, self.docinfo_id)


def platform_id(pad: ConjunctiveGraph):
    return [str(id) for id in pad.subjects(RDF.type, SCPO.Platform)]

