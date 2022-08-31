def print_graph(graph, max=10):
    print("-" * 80)
    for n, (s, p, o) in enumerate(graph):
        if n > max: break
        print(f"sub: {s}")
        print(f"rel: {p}")
        print(f"obj: {o}")
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
