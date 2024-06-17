
class Termination:
    """ 'pre'-processing """
    class NumList(tuple):
        def __str__(self, ):
            return "encoded num list"
    terminals = {
        int, float,
        str,
        bool,
        type(None), # weird
        # does json have datetime?
        NumList, # don't traverse these if matrix
        }
    terminals = tuple(terminals)
    @classmethod
    def visit(cls, p, k, v):
        def allnum(it): return all(isinstance(i, (float, int) ) for i in it)
        if k  == 'matrix':
            assert(isinstance(v, list))
            assert(allnum(v))
            return k, cls.NumList(v)
        elif k == 'data' and isinstance(v, list):
            assert(allnum(v))
            return k, cls.NumList(v)
        else:
            return True

    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap
        return remap(d, visit=cls.visit)


class Identification:
    idkeys = {'id'}
    
    @classmethod
    def enter(cls, p, k, v):
        ids = cls.idkeys
        def dicthasid(v): 
            for id in ids:
                if id in v:
                    return id
        if type(v) is dict:
            did = dicthasid(v)
            return {'id': v['id'] if did is not None else id(v)}, v.items()
        elif type(v) is list:
            return {'id': id(v)}, enumerate(v)
        else:
            assert(isinstance(v, Termination.terminals))
            return k, False
    
    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap
        return remap(d, enter=cls.enter)


class Tripling:
    """
    (identified) data -> triples
    """
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Triple:
        subject: 's'
        predicate: 'p'
        object: 'o'

        def __str__(self) -> str:
            return f"{self.subject} {self.predicate} {self.object}"
        
    class list(list):  #ordered set? TODO

        def __str__(self) -> str:
            _ = '\n'.join([str(i) for i in self])
            return _

    
    @classmethod
    def enter(cls, p, k, v):
        if isinstance(v, dict):
            assert('id' in v)
            def _(v):
                for ik, iv in v.items():
                    if isinstance(iv, dict):
                        #                   ptr to dict
                        yield from (cls.Triple(v['id'] , ik, iv['id'] ), iv )
                    else:
                        assert(isinstance(iv, Termination.terminals))
                        yield cls.Triple(v['id'], ik, iv)
            return cls.list(), enumerate(_(v))
        else:
            assert(isinstance(v, cls.Triple))
            # no nesting. no need to 'enter'
            return None, False
    
    @classmethod
    def map(cls, d, flatten=True):
        from boltons.iterutils import remap
        _ = remap(d, enter=cls.enter)
        if not flatten:
            return _
        else:
            _ = cls.flatten(_, seqtypes=(cls.list))
            _ = frozenset(_)
            _ = cls.list(_)
            return _
    
    @classmethod
    def flatten(cls, items, seqtypes=(list, tuple)):
        def flatten(items, seqtypes=seqtypes):
            #https://stackoverflow.com/questions/10823877/what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python
            try:
                for i, x in enumerate(items):
                    while isinstance(x, seqtypes):
                        items[i:i+1] = x
                        x = items[i]
            except IndexError:
                pass
            return items
        return flatten(items, seqtypes=seqtypes)


class RDFing:
    prefix = 'spkl'

    class Triple(Tripling.Triple):
        def __str__(self) -> str:
            return super().__str__()+'.'
    
    @classmethod
    def map(cls, d):
        # just need to take care of int predicates
        def _(d):
            for (s,p,o) in ((t.subject, t.predicate, t.object) for t in d):
                s = f'{cls.prefix}:{s}'
                p = f'rdf:_{p}' if isinstance(p, int) else f'{cls.prefix}:{p}'
                #      need to escape quotes
                if isinstance(o, str):
                    o = '"'+o.replace('"', r'\"')+'"'
                elif o is None:
                    o = 'rdf:nil'
                else:
                    o = str(o)
                yield cls.Triple(s,p,o)
        _ = Tripling.list(_(d))
        return _


from functools import cache
@cache
def bigjson():
    from json import load
    _ = load(open('./data.json'))
    return _

def propjson(n=10, p=10):
    pd = lambda pp=20: {f"pn{i}":f"pv{i}" for i in range(pp) }
    _ =  {f'pkey{i}': {'id':f"pid{i}", **pd(p) } for i in range(n) }
    _ = {'id':'r', **_ }
    return _

def test():
    #_ = propjson(20, 20)
    _ = bigjson()
    #_ = {'l': [1,2, {'lp': 33} ], 'p':3,  }
    #_ = {'p':3, 'lst': [0, {'pil':33}], 'matrix':[1,2] }
    _ = Termination.map(_)
    _ = Identification.map(_)
    _ = Tripling.map(_)
    _ = RDFing.map(_)
    return _


# downstream changes:
# mainly in Connectors:
# no need for complicated rdfList/*rest query
# 


if __name__ == '__main__':
    print(
    sum( len((test() )) for i in range(1)  )
    )