
from pathlib import Path
class Query:
    def __init__(self, p: Path, substitutions={}):
        p = Path(p)
        assert(p.exists())
        self.path = p
        self.substitutions = substitutions.copy()

    from functools import cached_property
    @cached_property
    def string(self):
        _ = self.path.read_text()
        from bim2rdf.utils.substitution import String
        _ = String(_)
        _ = _.substitue(self.substitutions)
        return _
    def __str__(self): return self.string
    

from speckle.meta import prefixes as spkl_prefixes
substitusions = {
    'x': 'xv',
    'prefix.spkl':      spkl_prefixes.concept.uri,
    'prefix.spkl.meta': spkl_prefixes.meta.uri,
    'model.arch.rooms&lights.name': 'architecture/rooms and lighting fixtures',
}

_ = Path(__file__).parent
_ = _.glob('**/*.rq')
_ = (Query(_, substitutions=substitusions) for _ in _)
shipped = tuple(_)
del _


if __name__ == '__main__':
    def _(out=Path('construct')):
        out = Path(out)
        for q in shipped:
            p = q.path.relative_to(Path(__file__).parent)
            p: Path = out / p
            p.parent.mkdir(parents=True, exist_ok=True)
            open(p, 'w').write(q.string)
        return out

    from fire import Fire
    Fire(_)