

def json():
    return {
        'k': [
            {'k': 3, 'kk': 'dil', 'kkk':True}
        ],
        'kk': { 'k': {'k': 'did'} },
        'ed': {}, 'el': [],
        'dwid': {
            'id': 33,
            'k': 'v'
        }
    }

def json():
    return {'k':'v', 'id':'id', 'l': [1,2,3, {'k':'v'}] }

def json():
    return {'id':'id', 'ID': 'ID', 'refid': 'id' }

def json():
    return {'id':'id', 'array': list(range(5))  }


def rdf():
    return """
    prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    _:2142013828288 _:id 2142013828288.
    _:2142013828288 _:k _:2142054851264.
    _:2142053379456 rdf:_0 _:2142054854336.
    _:2142053379456 _:id 2142053379456.
    _:2142054851264 _:id 2142054851264.
    _:2142054851264 _:k "asdf".
    _:2142054854336 _:id 2142054854336.
    _:2142054854336 _:k 3.
    _:2142054854336 _:kk "asdf".
    _:2142054860992 _:id 2142054860992.
    _:2142054860992 _:k _:2142053379456.
    _:2142054860992 _:kk _:2142013828288.
    """



def test():
    # from rdflib import Graph
    # a = rdf()
    # a = Graph().parse(data=a, format='text/turtle')

    _ = json()
    from json2rdf.json2rdf import to_rdf
    f = to_rdf(_, )
    print()
    print(f)
    #f = Graph().parse(data=f, format='text/turtle')

    #from rdflib.compare import isomorphic
    #assert(isomorphic(f, a))
    
