from .ontologies import included_def, ontology
from fire import Fire
from pathlib import Path

def import_(def_: Path = included_def):
    from .ontologies import import_ as f
    _ = f(Path(def_))
    return _

# integrated with 'main' bim2rdf cli
#from bim2rdf.cli import patch
main = ({'import': import_, 'write': ontology})
#exit(0)