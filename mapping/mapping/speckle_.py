# called it speckle_ b/c of naming issues
# 'from speckle' would be recursive

from speckle.graphql import queries, query
from speckle.objects import rdf
from shacl_gen import shacl
from ontologies import get as get_ontology
from . import mapping_dir

# (query>json) > ttl > mapping/validation via shacl > ttl

from pathlib import Path
def brick() -> Path:
    _ = mapping_dir / 'speckle' / 'brick.ttl'
    assert(_.exists())
    return _


def map():
    q = queries()
    q = q.objects
    d = query(q)
    d = rdf(d)
    m = brick() # mapping
    o = get_ontology('brick')
    _ = shacl(d, shacl=m, ontology=o)
    return _
    # gen data (rule effects)


if __name__ == '__main__':
    #from speckle.objects import rdf
    map()

