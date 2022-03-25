from attrs import frozen as dataclass
import rdflib
from abc import Mapping

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
    graph: rdflib.Graph

@dataclass
class OntologyCustomization:
    building: str
    ontology: Ontology

@dataclass
class SQLRDFMap:
    ontology: rdflib.Graph # not necessarily the ontology above
    mapping: Mapping
    properties: Properties
