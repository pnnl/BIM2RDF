
class Object: # Entity?
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


    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap 
        return remap(d,
                visit=cls.visit,
                enter=cls.enter,
                exit=cls.exit,
                )


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
        ids = {'referencedId', 'id'}
        def dicthasid(v): # dont mod dict
            for id in ids:
                if id in v:
                    return id
        if isinstance(v, dict):
            did = dicthasid(v)
            items = v.items() if did is None else ((k,v) for k,v in v.items() if k !=did )
            return Object(v[did] if did is not None else id(v), {}), items
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
                ptr_to_nested = [ ('{}', cls.Triple(v.subject, v.prediate, v.object.id)  )  ]
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
        def flatten(iterable, out):
            # some issue with dupes!!!
            # cant fig out.
            """``flatten_iter()`` yields all the elements from *iterable* while
            collapsing any nested iterables.

            >>> nested = [[1, 2], [[3], [4, 5]]]
            >>> list(flatten_iter(nested))
            [1, 2, 3, 4, 5]
            """
            for i in iterable:
                if isinstance(i, list):
                    flatten(i, out)
                else:
                    assert(isinstance(i, cls.Triple))
                    out.add(i)
                    
            # for item in iterable:
            #     if isinstance(item, list):
            #         yield from flatten_iter(item)
            #     else:
            #         yield item
        s = set()
        flatten(_, s) 
        #from tqdm import tqdm
        #_ = tqdm(_)
        _ = (s)
        return _


# RDFing
# obj that are sub


from functools import cache
def bigjson():
    from json import load
    _ = load(open('./data.json'))
    #_ = _['stream']['object']['data'] # ok
    #_ = _['stream']['object']['children']['objects'][0]['data']['parameters']
    return _


def propjson(n=10, p=10):
    pd = lambda pp=20: {f"pn{i}":f"pv{i}" for i in range(pp) }
    _ =  {f'pkey{i}': {'id':i,  **pd(p) } for i in range(n) }
    _ = {'id':'r', **_ }
    return _

def test():
    _ = propjson(10,20)
    _ = _.copy()
    #_ = [{'id':i, 'p':f"{i}"} for i in range(1)]
    _ = Identification.map(_)
    _ = Tripling.map(_)
    return _


def trec():
    ...


if __name__ == '__main__':
    print(
    sum( len((test() )) for i in range(1_000)  )
    )