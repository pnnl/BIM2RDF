from rdflib import Graph
from . import mapping_dir
from typing import Any, Iterator, Generator, Tuple, Literal, Union
from typing import overload
from pathlib import Path
from phantom import Phantom
from . import schema as s


from attrs import frozen as dataclass




@dataclass
class Building(s.Building): # can just ttl this?
    name:       str

    @overload
    @classmethod
    def make(cls, i: str)               -> 'Building': ...
    @overload
    @classmethod
    def make(cls, i: 'Building')        -> 'Building': ...
    @classmethod
    def make(cls, i: 'str | Building')  -> 'Building':
        return i if isinstance(i, Building) else Building(i)

    def uri(self, domain: str  = 'example.com') -> s.URI:
        return s.URI(f"http://{domain}/{self.name}")

    def prefix(self, domain: str = 'example.com') -> s.URI:
        _ = self.uri(domain)
        _ = _ + '/' if not _.endswith('/') else ''
        return s.URI(_)

    
@dataclass
class Prefix(s.Prefix):
    name:   s.KeyStr
    uri:    s.URI
    @classmethod
    def make(cls, frm='Prefix'):
        return frm


prefix = Prefix.make(Prefix(s.KeyStr('pnnl'), s.URI('http://example.com/')))


@dataclass
class MappingCallouts(s.MappingCallouts):
    prefix:     Prefix
    building:   Building

    @classmethod
    def make(cls, frm=Tuple[Prefix, Building], ) -> 'MappingCallouts':
        p, b = frm
        if p.uri.endswith(b.name) or p.uri[:-1].endswith(b.name):  return cls(p, b)
        else:
            return cls(
                        Prefix(
                            s.KeyStr(p.name),
                            s.URI(p.uri + b.name + '/') if p.uri.endswith('/') \
                            else s.URI(f"{p.uri}/{b.name}/")),
                        b)




@dataclass
class OntologyBase(s.OntologyBase):
    name:   str

    @property
    def graph(self):
        from ontologies import get
        return get(self.name)

    @classmethod
    def make(cls, frm: str):
        return cls(frm)

    @classmethod
    def s(cls, *p, **k) -> Generator['OntologyBase', None, None]:
        from ontologies import names
        for n in names: yield cls(n)


@dataclass
class OntologyCustomization(s.OntologyCustomization):
    base:               OntologyBase

    @overload
    @classmethod
    def make(cls, frm: str, /)                -> 'OntologyCustomization': ...
    @overload
    @classmethod
    def make(cls, frm: OntologyBase, /)       -> 'OntologyCustomization': ...
    @classmethod
    def make(cls, frm: str | OntologyBase )   -> 'OntologyCustomization':
        if      isinstance(frm, str):   return cls( OntologyBase.make(frm) )
        else:                           return cls(frm)
    
    
    @property
    def graph(self) -> Graph:
        def turtle_soup(loc: Path):
            g = s.Graph()
            for f in (f for f in ( loc ).iterdir() if f.suffix == '.ttl'):
                _ = s.Graph().parse(f)
                g += _
                for p, ns in _.namespaces(): g.bind(p, ns) # why do i have to do this (separately)?
            return g
        cstm = turtle_soup(mapping_dir / self.base.name)
        return cstm


@dataclass
class Ontology(s.Ontology):
    base:           OntologyBase
    customization:  OntologyCustomization
    
    @classmethod
    def make(cls, frm: 'str | Ontology', /)             -> 'Ontology':
        if isinstance(frm, Ontology): return frm
        oc = OntologyCustomization.make(frm)
        return cls(oc.base, oc)
    
    @property
    def graph(self) -> s.Graph:
        return self.base.graph + self.customization.graph



from typing import Protocol
class hasPathing(Protocol):
    @property
    def name(self)      -> str: ...
    @property
    def file_ext(self)  -> str: ...
class Writing(hasPathing):
    def path(self, dir: s.Dir) -> Path:
        return dir.absolute() / f"{self.name}.{self.file_ext}"


@dataclass
class OntologyWriting(s.OntologyWriting, Writing):
    ontology: Ontology
    @property
    def file_ext(self) ->   Literal['ttl']:      return 'ttl'
    @property
    def name(self) ->       Literal['ontology']: return 'ontology'

    @classmethod
    def make(cls, *p, **k) -> 'OntologyWriting':
        return cls(p[0])

    def write(self, dir: s.Dir) -> s.Path:
        self.ontology.graph.serialize(self.path(dir), format='turtle')
        return self.path(dir)

