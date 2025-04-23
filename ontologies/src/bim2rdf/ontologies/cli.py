from .ontologies import included_def, ontology
from pathlib import Path



def import_(definition: Path = included_def):
    from .ontologies import import_ as f
    _ = f(Path(definition))
    return _

def included_deff(out: Path|None = Path('ontology.def.ttl')):
    if out:
        _ = Path(out)
        _.write_text(included_def.read_text())
        return _
    else:
        assert(out is None)
        return included_def.read_text()


# integrated with 'main' bim2rdf cli
#from bim2rdf.cli import patch
main = ({'import': import_, 'write': ontology, 'included_def' :included_deff})
#exit(0)