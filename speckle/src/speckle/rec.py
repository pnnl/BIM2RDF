# using conversion using boltons.iterutils

from json import load
from boltons.iterutils import remap # get_path, research

# use remap to (k, v) -> (k, ttl)
# inplace string?


from functools import cache
@cache
def bigjson():
    _ = load(open('./data.json'))
    return _

class Object:
    __slots__ = 'id', 'data'
    def __init__(self, id, data={}) -> None:
        self.id = id
        self.data = data # self-refs :/
    
    def __repr__(self) -> str:
        return f"@{self.id} {repr(self.data)}"

    def update(self, items):
        self.data.update(items)


class MatrixList(list):
    def __str__(self, ):
        return "encoded matrix list"

terminals = {
    int, float, str,
    # datetime?
    #list, # don't traverse these if matrix
    MatrixList,
    }
terminals = tuple(terminals)


# need to identify.
# need a 'context' thing...
# ..to reach into a property at same level.

def json():
    return { "stream": {"id": 'sid', "object": {'id': 'oid',
    'p1': 123,
    'p2': 'abc',}},}


def json():
    return {'id': 1, 'p1':33, 'p': {'id': '2', 'pp': 3,  }  }


def json():
    return {'id':1, 'p':33, 'pl': {'id':2} }


def pth2triples(p):
    assert(len(p) == 2)
    assert(len(p) == 2)


def visit(p, k, v): # path, key, value
    # keep for transformations?
    return True
    # if isinstance(v, Object):
    #     return True
    # else:
    #     return False
    # do the transform here
    #return p+(k,), v
    # if isinstance(v, terminals):
    #     return k, str(v)
    # else:
    #     return k, v

def enter(p, k, v): # for creating 'parents'
    if isinstance(v, dict) and 'id' in v:
        o = Object(v.pop('id'))
        return o, v.items()
    elif isinstance(v, dict) and 'id' not in v:
        return dict(), v.items()
    else:
        isinstance(v, terminals)
        return v, False

def exit(p, k, v,
         new_obj, new_items):
    new_obj.update(new_items)
    return new_obj


def test():
    _ = bigjson()
    _ = remap(_,
            visit=visit, 
            enter=enter,
            exit=exit
            )
    return _
