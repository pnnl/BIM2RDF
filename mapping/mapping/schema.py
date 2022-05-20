from collections.abc import Mapping
from typing import Iterator, Literal, NewType, TypeVar, Generic, Sequence, Iterable
from typing import overload
from abc import ABC, abstractmethod # abstractXmethod: use @X(abstractXmethod)
# or just use protocols?
from phantom.base import Phantom
from rdflib import Graph
# or so that i don't even have to have rdflib specifically?
#Graph = TypeVar('Graph')

# learnings: zope.interface


#def abstractfield(f: Callable):
#    _ = abstractmethod(f)
#    _ = property(_)
#    return _
# need to use
#@property
#@abstractmethod
# for mypy to work


T = TypeVar('T',)
class Construtor(Generic[T], ABC): 
    @classmethod
    @abstractmethod
    def make(cls, *p, **k) -> T: ...


class ClassIterator(Generic[T], ABC):
    @classmethod
    @abstractmethod
    def s(cls, *p, **k) -> Iterable[T]: ...


class Validation(Generic[T], ABC):
    @abstractmethod
    def validate(self) -> bool:
        """arbitrary validations. mainly want to assert invariants."""

#V = TypeVar('V', bound='ValidatedConstruction')
class ValidatedConstruction(Validation[T], Construtor[T],):
    @classmethod
    def make(cls, *p, **k) -> T:
        m: T = cls.make_unvalidated(*p, **k)
        if m.validate(): return m
        else: raise TypeError

    @classmethod
    @abstractmethod
    def make_unvalidated(cls, *p, **k) -> T: ...



class Str(Generic[T], ABC):
    @abstractmethod
    def __str__(self) -> str: ...

#class Fantom(Phantom, abstract=True):...

class Base(ValidatedConstruction): ...

def is_property_name(s: str) -> bool: return s.startswith('jdbc.')
class DBPropertyName(str, Phantom, predicate=is_property_name): ...
def is_property(s: str) -> bool: return '=' in s
class PropertyStr(str, Phantom , predicate=is_property): ...

class DBProperty(Base, Str):
    @property
    @abstractmethod
    def name(self,)         -> DBPropertyName: ...
    @property
    @abstractmethod
    def value(self,)        -> str: ...
    
    @abstractmethod
    def __str__(self)       -> PropertyStr: ...

    def validate(self) -> bool: return True


class DBProperties(Base, Str):
    """ontop db config"""
    @property
    @abstractmethod
    def name(self)          -> DBProperty: ...
    @property
    @abstractmethod
    def url(self)           -> DBProperty:
        """it's called a url but not a web url"""
    @property
    @abstractmethod
    def driver(self)        -> DBProperty: ...
    @property
    @abstractmethod
    def user(self)          -> DBProperty: ...

    def validate(self) -> bool: return True

#@dataclass
#class DBPropertiesImpl(DBProperties):
    #notname: str #cant instantiate
    #name: int # can but is it typechecked?
#DBPropertiesImpl('sdf')

class OntopProperties(Base, Str):
    """ontop config"""
    @property
    @abstractmethod
    def inferDefaultDatatype(self) \
                            -> bool: ...
    
    def validate(self) -> bool: return True


class Properties(Base, Str):
    @property
    @abstractmethod
    def jdbc(self)          -> DBProperties: ...
    @property
    @abstractmethod
    def ontop(self)         -> OntopProperties: ...

    def validate(self) -> bool: return True


class OntologyBase(Base, ClassIterator):
    @property
    @abstractmethod
    def name(self)          -> str: ...
    @property
    @abstractmethod
    def graph(self)         -> Graph: ...

    def validate(self) -> bool:
        return self.name in {ob.name for ob in self.__class__.s()}


class Building(Base):
    @property
    @abstractmethod
    def name(self)              -> str: ...
    @abstractmethod
    def uri(self, prefix: str)  -> 'URI': ...

    def validate(self) -> bool: return True


class OntologyCustomization(Base):
    @property
    @abstractmethod
    def building(self)      ->  Building: ...
    @property
    @abstractmethod
    def base(self)          ->  OntologyBase: ...
    @property
    def graph(self)         ->  Graph: ...

    def validate(self) -> bool: return True


class Ontology(Base, ClassIterator):
    @property
    @abstractmethod
    def base(self)          -> OntologyBase: ...
    @property
    @abstractmethod
    def customization(self) -> OntologyCustomization | None: ...

    @property
    @abstractmethod
    def graph(self)         -> Graph: ...

    def validate(self) -> bool: return True


# 
def is_uri(s: str) -> bool: return s.startswith('http://') or s.startswith('https://')
class URI(str, Phantom, predicate=is_uri): ...
KeyStr =                    NewType('KeyStr', str) # no spaces in str?
Prefixes =                  Mapping[KeyStr, URI]

SQL =                       NewType('SQL', str)
templatedTTL =              NewType('templatedTTL', str)
class Map(Base, ClassIterator):
    @property
    @abstractmethod
    def id(self)            -> KeyStr: ...
    @property
    @abstractmethod
    def source(self)        -> SQL: ...
    @property
    @abstractmethod
    def target(self)        -> templatedTTL: ...

    def validate(self) -> bool: return True



def nonzeroseq(m: Sequence[Map]) -> bool: return True if len(m) else False
class Maps(Sequence[Map], Phantom, predicate=nonzeroseq): ...


class SQLRDFMap(Base, Str):
    """represents the obda file"""
    @property
    @abstractmethod
    def prefixes(self)      -> Prefixes | None: ...
    @property
    @abstractmethod
    def maps(self)          -> Maps: ...


from pathlib import Path
# maybe .exists and empty iterdir

def is_dir(p: Path) -> bool: return p.is_dir()
class Dir(Path, Phantom, predicate=is_dir): ...

class SQLRDFMapping(Base):
    """ related to the mapping 'action' """
    @property
    @abstractmethod
    def ontology(self)      -> Ontology: ...
    @property
    @abstractmethod
    def mapping(self)       -> Mapping: ...
    @property
    @abstractmethod
    def properties(self)    -> Properties:
        """represents 'input'"""

    @overload
    @classmethod
    @abstractmethod
    def writer(cls, part: 'Ontology',    dir: Dir)   -> 'OntologyWriting': ...
    @overload
    @classmethod
    @abstractmethod
    def writer(cls, part: 'Mapping',     dir: Dir)   -> 'MappingWriting': ...
    #https://github.com/python/mypy/issues/11488
    @overload
    @classmethod
    @abstractmethod
    def writer(cls, part: 'Properties',  dir: Dir)   -> 'PropertiesWriting': ...

    @classmethod
    @abstractmethod
    def writer(cls, part: Ontology | Mapping | Properties, dir: Dir) -> 'SQLRDFMapPartWriting':
        ...

    @abstractmethod
    def map(self)           -> None: # could be success/fail
        """the 'do' """

#FileExt = N*ewType('FileExt', str) # 'suffix' starts w/ .
FileExt = str
class SQLRDFMapPartWriting(ABC):
    @property
    @abstractmethod
    def of(self)            -> Ontology | SQLRDFMap | Properties: ...
    @property
    @abstractmethod
    def file_ext(self)      -> FileExt: ...
    @property
    @abstractmethod
    def name(self)           -> str: ...
    
    #@abstractmethod
    #def str(self)           -> str: ...
    @abstractmethod
    def write(self,
            dir: Dir)       -> None: ...

class OntologyWriting(Base, SQLRDFMapPartWriting,):
    @property
    @abstractmethod
    def of(self)            -> Ontology: ...           # learning: mypy: must be one of onto, sqlrdfmap, properties
    @property
    @abstractmethod
    def file_ext(self)      -> Literal['ttl']: ...     # learning: we're in type land.
                                # learning: can't do arbitrary exprs Literal[FileExt('ttl')]
    # nofile_ext = 3 # =3 learning. nice. mypy doesn't like it.
    # learning: implementation has to be like
    #@property
    #def file_ext(self) -> Literal['ttl']: return 'ttl'
    # couldnt check
    # learning = 'ttl'
    @property
    @abstractmethod
    def name(self)          -> Literal['ontology']: ...
class MappingWriting(Base, SQLRDFMapPartWriting):
    @property
    @abstractmethod
    def of(self)            -> SQLRDFMap: ...
    @property
    @abstractmethod
    def file_ext(self)      -> Literal['obda']: ...
    @property
    @abstractmethod
    def name(self)          -> Literal['maps']: ...
class PropertiesWriting(Base, SQLRDFMapPartWriting):
    @property
    @abstractmethod
    def of(self)            -> Properties: ...
    @property
    @abstractmethod
    def file_ext(self)      -> Literal['properties']: ...
    @property
    @abstractmethod
    def name(self)          -> Literal['sql']: ...


# but i want error if not implemented
# from classes import typeclass, AssociatedType
# class SQLRDFMapPartWriting(AssociatedType):
# @typeclass
# def file_ext(instance)      -> FileExt: ...
# @typeclass
# def name(instance)          -> str: ...
# @typeclass
# def string(instance)        -> str: ...
# @typeclass
# def write(instance,
#     file: TextIO)           -> None: ...


