# TODO: put in meta.py
base_uri = lambda: f"http://speckle.systems/" # urn:speckle:concept TODO
meta_uri = lambda: 'http://meta'              # urn:speckle:meta TODO


def object_uri(stream_id, object_id=''):
    return f"http://speckle.xyz/streams/{stream_id}/objects/{object_id}"


def namespaces():
    # spkl_arg 
    from ontologies import namespace
    from rdflib import URIRef
    return (
        namespace('spkl', URIRef(base_uri() )),
        namespace('spkl.meta', URIRef(meta_uri() ) )
    )

