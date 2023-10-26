

rectangles = """
@prefix ex: <http://example.com/ns#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:InvalidRectangle
	a ex:Rectangle .

ex:NonSquareRectangle
	a ex:Rectangle ;
	ex:height 2 ;
	ex:width 3 .
	
ex:SquareRectangle
	a ex:Rectangle ;
	ex:height 4 ;
	ex:width 4 . 
"""
rectangleRules = """
@prefix ex: <http://example.com/ns#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Rectangle
	a rdfs:Class, sh:NodeShape ;
	rdfs:label "Rectangle" ;
	sh:property [
		sh:path ex:height ;
		sh:datatype xsd:integer ;
		sh:maxCount 1 ;
		sh:minCount 1 ;
		sh:name "height" ;
	] ;
	sh:property [
		sh:path ex:width ;
		sh:datatype xsd:integer ;
		sh:maxCount 1 ;
		sh:minCount 1 ;
		sh:name "width" ;
	] ;
	sh:rule [
		a sh:TripleRule ;
		sh:subject sh:this ;
		sh:predicate rdf:type ;
		sh:object ex:Square ;
		sh:condition ex:Rectangle ;
		sh:condition [
			sh:property [
				sh:path ex:width ;
				sh:equals ex:height ;
			] ;
		] ;
	] .
    

"""



def pyshacl_rules(db: 'OxiGraph') -> 'Triples':
    from validation.shacl import graph, graph_diff
    from pyshacl.rules import apply_rules, gather_rules
    from pyshacl.functions import gather_functions, apply_functions
    from pyshacl.shapes_graph import ShapesGraph
    from rdflib import Graph
    _ = Graph()
    from io import StringIO
    _.parse(StringIO(rectangleRules))
    _ = graph(_)
    _ = ShapesGraph(_)
    _.shapes # finds rules. otherwise gather_rules errors
    shacl = _
    functions = gather_functions(shacl)
    rules =  gather_rules(shacl, iterate_rules=True)
    _ = db._store
    #_ = get_applicable(_)
    from mapping.conversions import og2rg, rg2og
    _ = og2rg(_)
    before = graph(_)
    after = graph(_)
    apply_functions(functions, after)
    apply_rules(rules, after, iterate=True)
    _ = graph_diff(before, after).in_generated
    _ = rg2og(_)
    from engine.triples import Triples
    _ = Triples(q.triple for q in _)
    return _


def test_shacl_rules():
    from pyoxigraph import Store
    db = Store()
    from io import StringIO
    db.bulk_load(StringIO(rectangles) , mime_type='text/turtle')
    from engine.triples import OxiGraph
    db = OxiGraph(db)
    assert(len(db))
    ts = pyshacl_rules(db)
    assert(list(ts))


