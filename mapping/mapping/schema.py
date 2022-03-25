from attrs import frozen as dataclass
from rdflib import Graph
from collections.abc import Mapping
from typing import Any

@dataclass
class DBProperties:
    name: str
    url: str
    driver: str
    user: str

@dataclass
class OntopProperties:
    inferDefaultDatatype: bool

@dataclass  
class Properties:
    jdbc:   DBProperties
    ontop:  OntopProperties


@dataclass
class Ontology:
    name: str
    graph: Graph

@dataclass
class OntologyCustomization:
    building: str
    ontology: Ontology

@dataclass
class SQLRDFMap:
    ontology: Graph # not necessarily the ontology above
    mapping: Mapping[str, Any]
    properties: Properties
