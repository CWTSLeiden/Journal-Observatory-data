from utils.utils import job_config as config


def print_verbose(message, end=None):
    if config.getboolean("main", "verbose", fallback=False):
        print(f"VERBOSE: {message}", end=end)


def print_graph(graph, max=10):
    print("-" * 80)
    try:
        for n, t in enumerate(graph.quads()):
            if n > max: break
            print_triple(t)
    except:
        for n, t in enumerate(graph):
            if n > max: break
            print_triple(t)


def print_triple(t):
    if len(t) == 3:
        s, p, o = t
        c = None
    else:
        s, p, o, c = t
    print(f"sub: {s}")
    print(f"rel: {p}")
    print(f"obj: {o}")
    if c: print(f"ctx: {c}")
    print("-" * 80)


def print_this(graph, pre=""):
    for n, uri in graph.namespaces():
        if n == "this":
            print(f"{pre}{uri}")
            return uri
    print(f"{pre}not found")


def print_namespaces(graph):
    for ns, uri in graph.namespaces():
        print(f"{ns :>10}{uri}")


def print_list(l):
    for n, item in enumerate(list(l)):
        print(f"{n}: {item}")
