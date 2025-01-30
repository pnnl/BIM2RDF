
def graph_diff(data, generated):
    # this is just adding naming to the tuple elements
    from collections import namedtuple
    GraphDiff = namedtuple('GraphDiff', ['in_both', 'in_data', 'in_generated'])
    from rdflib.compare import graph_diff as _graph_diff
    return GraphDiff(*_graph_diff(data, generated))

def copy(g1, g2=None):
    from rdflib import Graph
    if not g2: g2 = Graph() # to memory
    for t in g1: g2.add(t)
    return g2
