base_uri = f"http://speckle.systems/"
meta_uri = lambda: 'http://meta'


def object_uri(stream_id, object_id):
    return f"http://speckle.xyz/streams/{stream_id}/objects/{object_id}"


def namespaces():
    # spkl_arg 
    from ontologies import namespace
    from rdflib import URIRef
    return (
        namespace('spkl', URIRef(base_uri() )),
        namespace('spkl.meta', URIRef(meta_uri() ) )
    )

