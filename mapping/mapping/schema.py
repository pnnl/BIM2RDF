from typing import Literal, Sequence, Mapping
from typing import NewType
# or just use protocols?
from phantom.base import Phantom
from rdflib import Graph
# or so that i don't even have to have rdflib specifically?
#Graph = TypeVar('Graph')

# learnings: zope.interface

from typing import final
from .meta import ABC
from abc import abstractmethod



def is_property_name(s: str) -> bool: return s.startswith('jdbc.')
class DBPropertyName(str, Phantom, predicate=is_property_name): ...
def is_property(s: str) -> bool: return '=' in s
class PropertyStr(str, Phantom , predicate=is_property): ...

class DBProperty(ABC):
    @property
    @abstractmethod
    def name(self,)         -> DBPropertyName: ...
    @property
    @abstractmethod
    def value(self,)        -> str: ...
    
    @abstractmethod
    def __str__(self)       -> PropertyStr: ...

    @final
    def validate(self) -> bool:
        return True


class DBProperties(ABC):
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

    @final
    def validate(self) -> bool: return True


class OntopProperties(ABC):
    """ontop config"""
    @property
    @abstractmethod
    def inferDefaultDatatype(self) \
                            -> bool: ...
    
    @final
    def validate(self) -> bool: return True


class Properties(ABC):
    @property
    @abstractmethod
    def jdbc(self)          -> DBProperties: ...
    @property
    @abstractmethod
    def ontop(self)         -> OntopProperties: ...

    @final
    def validate(self) -> bool: return True


class OntologyBase(ABC):
    @property
    @abstractmethod
    def name(self)          -> str: ...
    @property
    @abstractmethod
    def graph(self)         -> Graph: ...

    @final
    def validate(self) -> bool:
        return True
        #return self.name in {ob.name for ob in self.__class__.s()}


class Graphs:
    @abstractmethod
    def graph(self)         -> Graph: ...


class Building(ABC):
    @property
    @abstractmethod
    def name(self)              ->  str: ...
    @abstractmethod
    def uri(self, prefix: str)  -> 'URI': ...

    @final
    def validate(self) -> bool: return True


class OntologyCustomization(Graphs, ABC):
    """'variables'"""
    @property
    @abstractmethod
    def base(self)          ->  OntologyBase: ...

    @property
    def graph(self)         ->  Graph: ...
    

    @final
    def validate(self) -> bool:
        return True


class Ontology(Graphs, ABC):
    @property
    @abstractmethod
    def base(self)          -> OntologyBase: ...
    @property
    @abstractmethod
    def customization(self) -> OntologyCustomization: ...

    @property
    @abstractmethod
    def graph(self)         -> Graph: ...

    @final
    def validate(self) -> bool:
        return self.base == self.customization.base


# 
def is_uri(s: str) -> bool:
    return (s.startswith('http://')     or  \
            s.startswith('https://') )  and \
            ('\\' not in s)
class URI(str, Phantom, predicate=is_uri): ...
def is_keystr(s: str) -> bool: return not (' ' in s)
class KeyStr(str, Phantom, predicate=is_keystr): ...

class Prefix(ABC):
    @property
    @abstractmethod
    def name(self)             -> KeyStr: ...
    @property
    @abstractmethod
    def uri(self)              -> URI: ...

    @final
    def validate(self) -> bool: return True

Prefixes =                  Mapping[KeyStr, URI]


SQL =                       NewType('SQL', str)
templatedTTL =              NewType('templatedTTL', str)
class Map(ABC):
    @property
    @abstractmethod
    def id(self)            -> KeyStr: ...
    @property
    @abstractmethod
    def source(self)        -> SQL: ...
    @property
    @abstractmethod
    def target(self)        -> templatedTTL: ...

    @final
    def validate(self) -> bool: return True


def nonzeroseq(m: Sequence[Map]) -> bool: return True if len(m) else False
class Maps(Sequence[Map], Phantom, predicate=nonzeroseq): ...


class MappingCallouts(ABC):
    """things we might care about in the mapping file"""
    @property
    @abstractmethod
    def prefix(self)        -> Prefix: ...
    @property
    @abstractmethod
    def building(self)      -> Building: ...

    @final
    def validate(self) -> bool:
        if not self.prefix.uri[:-1].endswith(self.building.name):
            return False
        else:
            return True


class SQLRDFMap(ABC):
    """represents the obda file"""
    @property
    @abstractmethod
    def prefixes(self)      -> Prefixes | None: ...
    @property
    @abstractmethod
    def maps(self)          -> Maps: ...
    
    #customizations:
    @property
    def callouts(self)      -> MappingCallouts | None: ...
    

    @final
    def validate(self) -> bool:
        def bdg_in_prefixes(bdg: Building, prefixes: Prefixes) -> bool:
            for ns, uri in prefixes.items():
                if uri.endswith(bdg.name):
                    return True
            return False
        def pfx_in_prefixes(pfx: Prefix, prefixes: Prefixes) -> bool:
            if pfx.name in prefixes: return True
            return False
        def pfx_in_map_targets(pfx: Prefix, maps: Maps) -> bool:
            if not maps:                                    return False
            if all((pfx.name in m.target) for m in maps):   return True
            else:                                           return False
        if self.callouts:
            if not self.prefixes:
                return False
            else:
                return \
                bdg_in_prefixes(    self.callouts.building, self.prefixes)  and \
                pfx_in_prefixes(    self.callouts.prefix,   self.prefixes)  and\
                pfx_in_map_targets( self.callouts.prefix,   self.maps)
        return False


from pathlib import Path
# maybe .exists and empty iterdir

def is_dir(p: Path) -> bool: return p.is_dir()
class Dir(Path, Phantom, predicate=is_dir): ...
def is_ttl(p: Path): return p.suffix == '.ttl'
class ttlFile(Path, Phantom, predicate=is_ttl): ...

class SQLRDFMapping(ABC):
    """ related to the mapping 'action' """
    @property
    @abstractmethod
    def ontology(self)      -> Ontology: ...
    @property
    @abstractmethod
    def mapping(self)       -> SQLRDFMap: ...
    @property
    @abstractmethod
    def properties(self)    -> Properties:
        """represents 'input'"""

    @final
    def validate(self) -> bool:
        return True

    # couldnt get the spec| impl slit to work.
    # but the individual writer maps might as well be an imlementation detail
    # @overload 
    # @abstractmethod
    # def writer(self, part: Ontology,    dir: Dir)   -> 'OntologyWriting': ...
    # @overload
    # @abstractmethod
    # def writer(self, part: SQLRDFMap,     dir: Dir)   -> 'MappingWriting': ...
    # #https://github.com/python/mypy/issues/11488
    # @overload
    # @abstractmethod
    # def writer(self, part: Properties,  dir: Dir)   -> 'PropertiesWriting': ...

    @abstractmethod
    def writer(self, part: Ontology | SQLRDFMap | Properties, ) \
            -> 'OntologyWriting | MappingWriting | PropertiesWriting': #'SQLRDFMapPartWriting':
        ...

    @abstractmethod
    def map(self, dir: Dir) -> ttlFile: 
        """the 'do' """


#FileExt = N*ewType('FileExt', str) # 'suffix' starts w/ .
FileExt = str
class SQLRDFMapPartWriting(ABC):
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
            dir: Dir)       -> Path: ...

    def validate(self) -> bool:
        return True

class OntologyWriting(SQLRDFMapPartWriting, ABC):
    @property
    @abstractmethod
    def ontology(self)      -> Ontology: ...
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

    def validate(self) -> bool:
        return True

class MappingWriting( SQLRDFMapPartWriting, ABC):
    @property
    @abstractmethod
    def mapping(self)       -> SQLRDFMap: ...
    @property
    @abstractmethod
    def file_ext(self)      -> Literal['obda']: ...
    @property
    @abstractmethod
    def name(self)          -> Literal['maps']: ...

    def validate(self) -> bool: return True

class PropertiesWriting(SQLRDFMapPartWriting, ABC):
    @property
    @abstractmethod
    def properties(self)    -> Properties: ...
    @property
    @abstractmethod
    def file_ext(self)      -> Literal['properties']: ...
    @property
    @abstractmethod
    def name(self)          -> Literal['sql']: ...

    def validate(self) -> bool: return True

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


