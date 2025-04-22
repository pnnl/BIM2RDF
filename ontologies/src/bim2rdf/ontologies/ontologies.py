from pathlib import Path

included_uri = 'http://pnnl/semint/imports'
def _():
    _ = Path(__file__).parent / 'def.ttl'
    assert(_.exists())
    assert(included_uri in _.read_text())
    return _
included_def = _(); del _

def import_(definition=included_def):
    assert(isinstance(included_def, Path))
    # best to run this in a separate process
    # bc oxigraph store gets locked
    # https://github.com/gtfierro/ontoenv-rs/issues/11

    from ontoenv import Config, OntoEnv
    cfg = Config([str(included_def.parent)], strict=False, offline=False)
    # make the environment
    env = OntoEnv(cfg)
    from rdflib import Graph
    dg = Graph()
    dg.parse(definition, format='turtle')
    env.import_dependencies(dg) # removes owl:imports
    return Path('.ontoenv/store.db')

class Turtle(str): ...
def ontology(*, store=Path('.ontoenv/store.db'), out=Path('ontology.ttl')) -> Turtle | Path:
    from pyoxigraph import Store
    os = Store((store))
    from pyoxigraph import RdfFormat
    from rdflib import Graph
    og = Graph()
    for g in os.named_graphs():
        _ = os.dump(from_graph=g, format=RdfFormat.TURTLE)
        og.parse(data=_, format='turtle')
    _ = og.serialize()
    _ = Turtle(_)
    if out:
        out = Path(out)
        out.write_text(_)
        return out
    else:
        return _

