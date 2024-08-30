# class Remapping
# composition  would involve composing terminals
# which are somehow the last thing in matching functions.

# this /might/ be done faster using parsing like Lark


class Termination:
    """ 'pre'-processing """
    class NumList(tuple):
        def __str__(self, ):
            return "encoded num list"
        
        @staticmethod
        def data_encode(d: list) -> str:
            from numpy import savez_compressed as save, array
            #from numpy import save
            _ = d
            _ = array(d, dtype='float16')
            from io import BytesIO
            def sv(d):
                _ = BytesIO()
                #save(_, d)
                save(_, array=d)
                return _
            _ = sv(_)
            _.seek(0)
            _ = _.read()
            from base64 import b64encode
            _ = b64encode(_)
            _ = _.decode()
            return _
        @staticmethod
        def data_decode(d: str) -> 'array':
            _ = d
            from base64 import b64decode
            _ = b64decode(_,)
            from numpy import load
            from io import BytesIO
            _ = BytesIO(_)
            _ = load(_)
            _ = _['array']
            return _
        
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
    ref_idkeys = {
        'referencedId',
        'connectedConnectorIds'}

    from dataclasses import dataclass
    @dataclass(frozen=True)
    class ID:
        value: int | str # usually
        def __str__(self) -> str:
            return str(self.value)
    
    terminals = {Termination.terminals}|{ID}
    terminals = tuple(terminals)
    
    @classmethod
    def visit(cls, p, k, v):
        # interpret identifier cases
        if k in cls.ref_idkeys:
            if isinstance(v, (int, str)):
                return k, cls.ID(v)
        if p: # example connectedIds: [id1,id2,id3]
            if any(k in cls.ref_idkeys for k in p):
                if isinstance(v, (int, str)):
                    return k, cls.ID(v)
        return True
    
    @classmethod
    def enter(cls, p, k, v):
        ids = cls.idkeys
        def dicthasid(v):
            for id in ids:
                if id in v:
                    return id
        if type(v) is dict:
            did = dicthasid(v)
            return {'id': cls.ID(v['id']) if did is not None else cls.ID(id(v)) }, ((k,v) for k,v in  v.items() if k !=did)
        elif type(v) is list:
            return {'id': cls.ID(id(v)) }, enumerate(v)
        else:
            assert(isinstance(v, cls.terminals ))
            return k, False        
    
    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap
        return remap(d, enter=cls.enter, visit=cls.visit)



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
    def visit(cls, p, k, v):
        if isinstance(v, cls.Triple):
            if v.predicate in Identification.idkeys:
                if isinstance(v.object, Identification.ID):
                    return k, cls.Triple(v.subject, v.predicate, v.object.value)
        return True
    
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
                        assert(isinstance(iv, Identification.terminals ))
                        yield cls.Triple(v['id'], ik, iv)
            return cls.list(), enumerate(_(v))
        else:
            assert(isinstance(v, cls.Triple))
            # no nesting. no need to 'enter'
            return None, False
    
    @classmethod
    def map(cls, d, flatten=True):
        from boltons.iterutils import remap
        _ = remap(d, enter=cls.enter, visit=cls.visit)
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

    class Triple(Tripling.Triple):
        def __str__(self) -> str:
            if isinstance(self.subject, Tripling.Triple):
                #                     but take out the dot
                s = f"<<{str(self.subject)[:-1]}>>"
            else:
                s = str(self.subject)
            if isinstance(self.object, Tripling.Triple):
                o = f"<<{str(self.object)[:-1]}>>"
            else:
                o = str(self.object)
            return f"{s} {self.predicate} {o}."
    class list(Tripling.list):
        prefix = 'spkl'
        from . import base_uri
        base_uri = base_uri()
        meta_prefix = 'meta'
        meta_uri = "http://meta"

        def __str__(self) -> str:
            _ = f'prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n'
            _ = _ + f'prefix {self.prefix}: <{self.base_uri}>  \n'
            _ = _ + f'prefix {self.meta_prefix}: <{self.meta_uri}>  \n\n'
            _ = _ + super().__str__()
            return _
    
    @classmethod
    def triple(cls, s, p, o):
        m = {True: 'true', False:'false', None: '\"null\"'} # not rdf:nil which is specific to a rdf:List
        from types import NoneType
        # SUBJECT
        assert(isinstance(s, Identification.ID))
        s = f'{cls.list.prefix}:{s}'

        # PREDICATE
        # just need to take care of int predicates
        if isinstance(p, int):
            p = f'rdf:_{p}'
        else:
            assert(isinstance(p, str))
            p = p.replace(' ', '_')
            # create legal by dropping non alpha num
            # url encodeing?
            p = ''.join(c for c in p if c.isalnum() or c == '_' )
            p = f'{cls.list.prefix}:{p}'
        
        # OBJECT
        #      need to escape quotes
        if isinstance(o, str):
            # dont want to encode('unicode_escape').decode()
            # to not lose unicode chars
            # escape all the backslashes, first..
            o = o.replace("\\", "\\\\")
            # /then/ ...
            # escape spacing things
            o = o.replace('\n', '\\n')
            o = o.replace('\r', '\\r')
            o = o.replace('\f', '\\f')
            o = o.replace('\t', '\\t')
            # inner quotes
            o = o.replace('"', '\\"')
            # outer quote
            o = '"'+o+'"'
        elif isinstance(o, (bool, NoneType)): # https://github.com/w3c/json-ld-syntax/issues/258
            o = m[o]
        elif isinstance(o, Termination.NumList):
            o = '"'+str(o)+'"'
        elif isinstance(o, Identification.ID):
            o = f'{cls.list.prefix}:{o}'
        else:
            o = str(o)
        return cls.Triple(s,p,o)

    @classmethod
    def visit(cls, v):
        assert(isinstance(v, Tripling.Triple))
        # meta tripling
        # just do one-level in
        if isinstance(v.subject, Tripling.Triple):
            s = cls.triple(v.subject.subject,
                           v.subject.predicate,
                           v.subject.object)
        else:
            s = v.subject
        p = v.predicate
        if isinstance(v.object, Tripling.Triple):
            o = cls.triple(v.object.subject,
                           v.object.predicate,
                           v.object.object)
        else:
            o = v.object
        if p == cls.list.meta_uri:
            p = f"{cls.list.meta_prefix}:"
            return cls.Triple(s, p, o)
        else:
            return cls.triple(s,p,o)

    @classmethod
    def map(cls, d, meta=[], ):
        if meta:
            from itertools import product
            d = product(meta, d)
            d = map(lambda mt: Tripling.Triple(mt[0], cls.list.meta_uri, mt[1]), d)
        _ = map(cls.visit, d)
        _ = cls.list(_)
        return _



def to_rdf(data: str | dict,
           meta: str | dict = {},
           asserted=True,
           ):
    d = data
    m = meta
    def triples(data):
        _ = data
        _ = Termination.map(_)
        _ = Identification.map(_)
        _ = Tripling.map(_)
        return _
    if isinstance(d, str):
        from json import loads
        d = loads(d)
    if m:
        if isinstance(m, str):
            from json import loads
            m = loads(m)

    d = triples(d)    
    if m:
        m = triples(m)
        m = RDFing.map(d, meta=m)
        if asserted:
            # just pull rdfed
            d = frozenset([t.object for t in m])
        else:
            d = frozenset()
        # asserted 'data' triples + meta triples
        d = RDFing.list(frozenset(m) | d )
    else:
        d = RDFing.map(d)
    d = str(d)
    return d



if __name__ == '__main__':
    from pathlib import Path
    from .data import get_json

    def json(stream_id, object_id,
             path=Path('data.json'), ):
        """gets json"""
        _ = get_json(stream_id, object_id)
        path = Path(path)
        from json import dump
        dump(_, open(path, 'w'),)
        return path
    
    def ttl(stream_id, object_id,
            path=Path('data.ttl'),):
        """gets json and converts it to ttl"""
        path = Path(path)
        _ = get_json(stream_id, object_id)
        _ = to_rdf(_)
        open(path, 'w').write(_)
        return path

    import fire
    fire.Fire({
        'json': json,
        'ttl': ttl,})

