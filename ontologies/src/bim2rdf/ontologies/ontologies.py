from pathlib import Path

included_uri = 'http://pnnl/semint/imports'
def _():
    _ = Path(__file__).parent / 'def.ttl'
    assert(_.exists())
    assert(included_uri in _.read_text())
    return _
included_def = _(); del _

def import_(
        definition=included_def, 
        out=Path('ontology.ttl')
        ):
    assert(isinstance(included_def, Path))
    # best to run this in a separate process
    # bc oxigraph store gets locked
    # https://github.com/gtfierro/ontoenv-rs/issues/11
    from ontoenv import OntoEnv
    env = OntoEnv('.',
            search_directories=[str(definition.parent)],
            create_or_use_cached=False, temporary=True,
            strict=False,
            offline=False,)
    from rdflib import Graph
    g = Graph()
    from bim2rdf.core.rdf import Prefix
    for p in Prefix.s(): g.bind(p.name, p.uri)
    env.get_closure(included_uri, destination_graph=g)
    g.serialize(out, format='text/turtle')
    return out

