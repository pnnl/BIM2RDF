from engine.triples import (
        Engine as _Engine, Rule, Rules,
        Triples,
        OxiGraph)


class SelectQuery:
    def __init__(self, query: str) -> None:
        self.string = query
    
    def __str__(self) -> str:
        return self.string

    @property
    def spec(self):
        return self.string

from pathlib import Path
class SelectQueryRule(Rule):
    def __init__(self, spec: SelectQuery | Path ) -> None:
        if isinstance(spec, Path):
            self.path = spec.absolute()
            spec = open(spec).read()
            spec = SelectQuery(spec)
        else:
            assert(isinstance(spec, str))

        self._spec = spec
    
    @property
    def spec(self) -> SelectQuery:
        return self._spec

    def __add__(self, rule: 'Rule') -> 'Rules':
        return Rules([self, rule])

    def meta(self, ) -> Iterable[g.Triple]:
        # can add query str. or triples!
        # TODO
        yield from []

    def do(self, db: OxiGraph) -> Iterable[g.Triple]:
        _ = db._store.query(str(self.spec))
        assert(isinstance(_, g.QueryTriples))
        yield from self.add_star_meta(_)


class ConstructRule(_ConstructRule):

    def __init__(self, path) -> None:
        from pathlib import Path
        path = Path(path).absolute()
        self.path = path
        # for the mapping case, we're starting from the file
        spec = open(path).read()
        super().__init__(spec)
    
    @property
    def name(self):
        from project import root
        _ = self.path.relative_to(root).as_posix()
        return _
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def meta(self, ) -> Iterable[Triple]:
        yield from super().meta()
        p = meta_prefix
        fp = self.path.parts[-2:] # get the file plus its parent dir
        fp = '/'.join(fp)
        yield from [Triple(
                # TODO: add a name here to be like the pyrule
                #        watch that the fn is unique enough
                NamedNode(f'{p}/constructquery'),
                NamedNode(f'{p}/constructquery#name'),
                rdfLiteral(str(self.name))
                     )]