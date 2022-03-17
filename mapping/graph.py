import rdflib

def get_223p():
    from pathlib import Path
    g = rdflib.Graph()
    for f in (f for f in (Path('.') / 'reference-223p').iterdir() if f.suffix == '.ttl'):
        g += rdflib.Graph().parse(f)
    return g


#%%
namespaces = {
    # 'xml':      'http://www.w3.org/XML/1998/namespace',
    # 'rdf':      'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    # 'rdfs':     'http://www.w3.org/2000/01/rdf-schema#',
    # 'xsd':      'http://www.w3.org/2001/XMLSchema#',
    # 'owl':      'http://www.w3.org/2002/07/owl#',
    # 'skos':     'http://www.w3.org/2004/02/skos/core#',
    # 'qudt':     'http://qudt.org/schema/qudt/',
    # 'shacl':    'http://www.w3.org/ns/shacl#',
    # 'dc':       'http://purl.org/dc/terms#',
    # 'schema':   'http://schema.org/',
    # 'our' stuff
    'brick':    'https://brickschema.org/schema/Brick#',
    'bdg':		'http://example.org/building',
}



def namespace(g):
    for p, iri in namespaces.items():
        g.namespace_manager.bind(p,   iri, override=True, replace=True)
    return g

def fix(g):
    # https://github.com/BrickSchema/Brick/issues/308
    from rdflib import OWL as owl
    from rdflib import RDF as rdf
    from rdflib import URIRef
    v=URIRef('https://brickschema.org/schema/Brick#value')
    #g.remove( (v, rdf.type, owl.DatatypeProperty) )
    g.remove( (v, rdf.type, owl.ObjectProperty) )
    return g


#def mod(g):
    # can do all this in the mapping
    # add luminaire 'types'
    #g.add()

def export(g, fn='mapped'):
    from pathlib import Path
    o = Path('.') / f'{fn}.ttl'
    g.serialize(str(o), format='turtle')
    return o.absolute()



    
