# class Remapping
# composition  would involve composing terminals
# which are somehow the last thing in matching functions.


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
            return super().__str__()+'.'
    class list(Tripling.list):
        prefix = 'spkl'
        from . import base_uri
        base_uri = base_uri()

        def __str__(self) -> str:
            _ = f'prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n'
            _ = _ + f'prefix {self.prefix}: <{self.base_uri}>  \n\n'
            _ = _ + super().__str__()
            return _
    
    @classmethod
    def map(cls, d):
        def _(d):
            m = {True: 'true', False:'false', None: '\"null\"'} # not rdf:nil which is specific to a rdf:List
            from types import NoneType
            for (s,p,o) in ((t.subject, t.predicate, t.object) for t in d):
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
                yield cls.Triple(s,p,o)
        _ = RDFing.list(_(d))
        return _


def to_rdf(d: str | dict):
    if isinstance(d, str):
        from json import loads
        d = loads(d)
    _ = d
    _ = Termination.map(_)
    _ = Identification.map(_)
    _ = Tripling.map(_)
    _ = RDFing.map(_)
    _ = str(_)
    return _


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


