

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
    int, float, str,
    type(None), # weird
    # does json have datetime?
    MatrixList, # don't traverse these if matrix
    }
terminals = tuple(terminals)



class Remapping:

    def __init__(self, d) -> None:
        self.data = d

    @classmethod
    def map(cls, j):
        from boltons.iterutils import remap 
        return remap(j,
                visit=cls.visit,
                enter=cls.enter,
                exit=cls.exit,)
    
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
        def dicthasid(v):
            if isinstance(v, dict):
                if 'id' in v:
                    return v.pop('id')
                if 'referencedId' in v:
                    return v.pop('referencedId')
            else:
                return False
        # dict w/ id -> Object
        if did:=dicthasid(v):
            o = Object(did, {})
            return o, v.items()
        elif isinstance(v, dict):
            return Object(id(v), {}), v.items()
        elif isinstance(v, list):
            #from uuid import uuid4 as uid.
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
                ptr_to_nested = [ (0, cls.Triple(v.subject, v.prediate, v.object.id)  )  ]
                nested = ((ik, cls.Triple(v.object.id, ik, iv)) for ik,iv in iter(v.object) )
                return [], chain(ptr_to_nested, nested)
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
    def map(cls, d):
        _ = super().map(d)
        from boltons.iterutils import flatten#, flatten_iter
        _ = flatten(_)
        return _


from functools import cache
@cache
def bigjson():
    from json import load
    _ = load(open('./data.json'))
    return _


def json():
    return { "stream": {"id": 'sid', "object": {'id': 'oid',
    'p1': 123,
    'p2': 'abc',}},}

def json():
    # connector triple is   (1, lp, 2)
    return {'id':1, 'p': 3, 'lp': {'id': 2, 'p': 'np'}  }



def test():
    _ = json()
    _ = Identification.map(_)
    #return _
    _ = Tripling.map(_)
    return _

# 1. id
# 2. triple (in structure)
# 3. flatten (take out structure)
# 4. to str