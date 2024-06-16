

class Object: # entity?
    __slots__ = 'id', 'data'
    def __init__(self, id, data) -> None:
        self.id = id
        self.data = data # self-refs :/
    
    def __repr__(self) -> str:
        return f"@{self.id} {repr(self.data)}"

    def update(self, items):
        if isinstance(self.data, list):
            self.data.extend(v for k,v in items)
        else:
            assert(isinstance(self.data, dict))
            self.data.update(items)
    
    def __iter__(self):
        if isinstance(self.data, type(self)):
            yield from self.data
        elif isinstance(self.data, list):
            yield from enumerate(self.data)
        else:
            assert(isinstance(self.data, dict))
            yield from self.data.items()


class MatrixList(list):
    def __str__(self, ):
        return "encoded matrix list"

terminals = {
    int, float,
    str,
    bool,
    type(None), # weird
    # does json have datetime?
    MatrixList, # don't traverse these if matrix
    }
terminals = tuple(terminals)



class Remapping:

    def __init__(self, d) -> None:
        self.data = d

    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap 
        return remap(d,
                visit=cls.visit,
                enter=cls.enter,
                exit=cls.exit,
                )
    
    def __call__(self):
        return self.map(self.data)


class Identification(Remapping):
    """
    json -> objects with id
    """
    @classmethod
    def visit(cls, p, k, v): # path, key, value
        # keep for transformations?
        return True
    
    @classmethod
    def enter(cls, p, k, v):
        # for creating 'parents'
        # and id'ing things
        def dicthasid(v): # dont mod dict
            if ('referencedId' in v) or ('id' in v):
                return v
            else:
                v = v.copy()
                v['id'] = id(v)
            return v
        if isinstance(v, dict):
            v = dicthasid(v)
            return Object(id(v), {}), v.items()
        elif isinstance(v, list):
            #from uuid import uuid4 as uid
            # python already creates an id. just use it
            return Object(id(v), []), enumerate(v)  # why do i have to enum?
        else:
            assert(isinstance(v, terminals))
            return v, False

    @classmethod
    def exit(cls, p, k, v,
            new_obj, new_items):
        if isinstance(new_obj, Object):
            new_obj.update(new_items)
        else:
            raise Exception('not handled')
            #assert(isinstance(new_obj, list))
            #new_obj.extend(v for i,v in new_items)
        return new_obj
    

class Tripling(Remapping):
    """
    (identified) objects -> triples
    """
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Triple:
        subject: 's'
        prediate: 'p'
        object: 'o'

        def __str__(self) -> str:
            return f"{self.subject} {self.prediate} {self.object}."

    @classmethod
    def visit(cls, p, k, v):
        return True
    
    @classmethod
    def enter(cls, p, k, v):
        from itertools import chain
        if isinstance(v, Object):
            return [], ((ik, cls.Triple(v.id, ik, iv)) for ik,iv in iter(v) )
        else:
            assert(isinstance(v, cls.Triple))
            if isinstance(v.object, Object): # some "nesting"
                ptr_to_nested = []# [ ('sdfsdff', cls.Triple(v.subject, v.prediate, v.object.id)  )  ]
                nested = ((ik, cls.Triple(v.object.id, ik, iv)) for ik,iv in iter(v.object) )
                return [], (chain(ptr_to_nested, nested))
            else:
                return v, False

    @classmethod
    def exit(cls, p, k, v,
            new_obj, new_items):
        if isinstance(new_obj, list):
            new_obj.extend(v for k,v in new_items)
        else:
            raise Exception('not handled')
        return new_obj
    
    @classmethod
    def map(cls, d, progress=False):
        _ = super().map(d) # just creating triples (in nesting) is fast!
        def xflatten_iter(iterable, did=set()):
            # most intensive part for some reason
            # from boltons.iterutils import flatten_iter as flatten
            # more optimized of
            """``flatten_iter()`` yields all the elements from *iterable* while
            collapsing any nested iterables.

            >>> nested = [[1, 2], [[3], [4, 5]]]
            >>> list(flatten_iter(nested))
            [1, 2, 3, 4, 5]
            """
            for i in iterable:
                if isinstance(i, list):
                    yield from flatten_iter(i, did=did)
                else:
                    assert(isinstance(i, cls.Triple))
                    if i not in did:
                        did.add(i)
                        yield 1
                    else:
                        sdf
                        continue
            # for item in iterable:
            #     if isinstance(item, list):
            #         yield from flatten_iter(item)
            #     else:
            #         yield item
        from boltons.iterutils import flatten_iter
        _ = flatten_iter(_)
        #from tqdm import tqdm
        #_ = tqdm(_)
        _ = list(_)
        return _



# RDFing
# obj that are sub



def json():
    return { "stream": {"id": 'sid', "object": {'id': 'oid',
    'p1': 123,
    'p2': 'abc',}},}

def json():
    # connector triple is   (1, lp, 2)
    return {'id':1, 'p': 3, 'lp': {'id': 2, 'p': 'np'}  }

def json():
    return {'id':3, 'l': [1,2, {'id': 5, 'pl': 'p'}  ] }


from functools import cache
@cache
def bigjson():
    from json import load
    _ = load(open('./data.json'))
    #_ = _['stream']['object']['data'] # ok
    #_ = _['stream']['object']['children']['objects'][0]['data']['parameters']
    return _

@cache
def badjson():
    from json import load
    return load(open('./bad.json'))
    _ = '{"id": 3, "p": "pp" }'
    from json import loads
    _ = loads(_)
    return _

def test():
    _ = badjson()
    _ = Identification.map(_)
    _ = Tripling.map(_)
    return _

