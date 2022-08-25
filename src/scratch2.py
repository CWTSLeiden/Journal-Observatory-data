from utils import *
from namespace import *
from rdflib import *

ns1 = JobNamespace(uuid=True)
print_this(ns1, pre="ns1: ")

g1 = init_graph(id="g1")
g1.bind("this", ns1.THIS, override=True)
print_this(g1, pre="g1:  ")

ns2 = JobNamespace(uuid=True)
print_this(ns2, pre="ns2: ")

g2 = init_graph(id="g2")
g2.bind("this", ns2.THIS, override=True)
print_this(g2, pre="g2:  ")
