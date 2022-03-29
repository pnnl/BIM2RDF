from attrs import frozen as dataclass
from rdflib import Graph
from collections.abc import Mapping 
from typing import Any, Callable, TypeVar, Generic
from abc import ABC, abstractmethod, abstractclassmethod


def abstractfield(f: Callable):
    _ = abstractmethod(f)
    _ = property(_)
    return _



T = TypeVar('T')
class Construtor(Generic[T], ABC): 
    @abstractclassmethod
    def make(cls, *p, **k) -> T: ...


@dataclass # looks like i have to put this here
class Base(Construtor): pass

class DBProperties(Base):
    @abstractfield
    def name(self)          -> str: ...
    @abstractfield
    def url(self)           -> str: ...
    @abstractfield
    def driver(self)        -> str: ...
    @abstractfield
    def user(self)          -> str: ...


#@dataclass
#class DBPropertiesImpl(DBProperties):
    #notname: str #cant instantiate
    #name: int # can but is it typechecked?
#DBPropertiesImpl('sdf')


class OntopProperties(Base):
    @abstractfield
    def inferDefaultDatatype(self) \
                            -> bool: ...


class Properties(Base):
    @abstractfield
    def jdbc(self)          -> DBProperties: ...
    @abstractfield
    def ontop(self)         -> OntopProperties: ...


class OntologyBase(Base):
    @abstractfield
    def name(self)          -> str: ...
    @abstractfield
    def graph(self)         -> Graph: ...


class OntologyCustomization(Base):
    @abstractfield
    def building(self)      ->  str: ...
    @abstractfield
    def base(self)          ->  OntologyBase: ...


class Ontology(Base):
    @abstractfield
    def base(self)          -> OntologyBase: ...
    @abstractfield
    def customization(self) -> OntologyCustomization: ...

    @abstractmethod
    def graph(self)         -> Graph: ...


class SQLRDFMap(Base):
    @abstractfield
    def ontology(self)      -> Ontology: ...
    @abstractfield
    def mapping(self)       -> Mapping[str, Any]: ... # todo typeddict for further
    @abstractfield
    def properties(self)    -> Properties: ...

