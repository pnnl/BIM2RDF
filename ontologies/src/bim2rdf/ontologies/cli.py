from .ontologies import included_def
from pathlib import Path

from .ontologies import import_

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
    'import': import_, })
#exit(0)