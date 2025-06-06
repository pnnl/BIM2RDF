from .ontologies import included_def, ontology
from pathlib import Path


def import_(definition: Path = included_def):
    """go through compilation process"""
    from .ontologies import import_ as f
    _ = f(Path(definition))
    return _

def included_definition(out: Path|None = Path('ontology.def.ttl')):
    """print out included definition"""
    if out:
        _ = Path(out)
        _.write_text(included_def.read_text())
        return _
    else:
        assert(out is None)
        return included_def.read_text()



# integrated with 'main' bim2rdf cli
#from bim2rdf.cli import patch
main = ({ # steps order
    'included_definition' :included_definition,
    'import': import_,
    'write': ontology, })
#exit(0)