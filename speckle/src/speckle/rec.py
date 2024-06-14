# using conversion using boltons.iterutils

from json import load
import select
from boltons.iterutils import get_path, remap, research
# #, # remap maybe dont need it. do it through research

# use remap to (k, v) -> (k, ttl)
# inplace string?



class MatrixList(list):
    def __str__(self, ):
        return "matrix list"

terminals = {
    int, float, str,
    # datetime?
    #list, # don't traverse these if matrix
    MatrixList,
    }
terminals = tuple(terminals)


from functools import cache
@cache
def json():
    return load(open('./data.json'))


class Object:
    __slots__ = 'id', 'data'
    def __init__(self, id, data={}) -> None:
        self.id = id
        self.data = data
    
    def __repr__(self) -> str:
        return f"@{self.id} {repr(self.data)}"

    def update(self, items):
        self.data.update(items)
        

# need to identify.
# need a 'context' thing...
# ..to reach into a property at same level.

def json():
    return { "stream": {"id": 'sid', "object": {'id': 'oid',
    'p1': 123,
    'p2': 'abc',}},}


def json():
    return {'id': '1', 'p': {'id': '2', 'pp': 3 }  }


def pth2triples(p):
    assert(len(p) == 2)
    assert(len(p) == 2)


def visit(p, k, v): # path, key, value
    return True
    # keep for transformations?
    if isinstance(v, Object):
        return True
    else:
        return False
    # do the transform here
    return p+(k,), v
    if isinstance(v, terminals):
        return k, str(v)
    else:
        assert(isinstance(v, list))
        return k, v


def enter(p, k, v): # for creating 'parents'
    if isinstance(v, dict):
        o = Object(v.pop('id'))
        return o, v.items()
    else:
       assert(isinstance(v, terminals))
       return v, False
    
def exit(p, k, v, new_obj, new_items):
    new_obj.update(new_items)
    return new_obj


def test():
    _ = json()
    _ = remap(_,
            visit=visit, 
            enter=enter,
            exit=exit
            )
    return _
