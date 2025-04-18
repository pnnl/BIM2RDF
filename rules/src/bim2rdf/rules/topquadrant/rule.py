from ..rule import Rule
Query = str
class _TQ(Rule):
    def __init__(self, *, data: Query, shapes: Query):
        assert('construct' in data.lower())
        assert('construct' in shapes.lower())
        from bim2rdf.core.queries import SPARQLQuery
        data:str =   str(SPARQLQuery(data))
        shapes:str = str(SPARQLQuery(shapes))
        self.tqdata = data
        self.shapes = shapes

    def __repr__(self):
        nm = self.__class__.__name__
        qr = lambda q: q[-50:].replace('\n', '')
        return f"{nm}(data={qr(self.tqdata)}, shapes={qr(self.shapes[-50:])})"

    from functools import cached_property
    @cached_property
    def spec(self): return {'data': self.tqdata, 'shapes': self.shapes}

    from pyoxigraph import Store
    def prep(self, db:Store):
        class inputs:
            from pathlib import Path
            dp = Path('data.tq.tmp.ttl')
            sp = Path('shapes.tq.tmp.ttl')
            del Path
        def write(pth, query):
            from pyoxigraph import serialize, RdfFormat
            _ = db.query(query, )
            _ = serialize(_, pth, format=RdfFormat.TURTLE)
            return _
        
        write(inputs.dp, self.tqdata)
        write(inputs.sp, self.shapes)
        return inputs
        # yield inputs  # context mgr? https://github.com/pnnl/pytqshacl/issues/5
        # inputs.dp.unlink()
        # inputs.sp.unlink()

    def data(self, db: Store):
        if 'infer' in self.__class__.__name__.lower():
            from pytqshacl import infer as tq
        else:
            assert('valid' in self.__class__.__name__.lower())
            from pytqshacl import validate as tq
        inputs = self.prep(db)
        _ = tq(inputs.dp, shapes=inputs.sp)
        inputs.dp.unlink()
        inputs.sp.unlink()
        from pyoxigraph import parse, RdfFormat
        _ =  parse(_.stdout, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        yield from _

class TopQuadrantInference(_TQ):
    from bim2rdf.core.rdf import Prefix
    meta_prefix = Prefix('tq.inf.meta', "urn:meta:bim2rdf:TopQuadrantInference:")
class TopQuadrantValidation(_TQ):
    from bim2rdf.core.rdf import Prefix
    meta_prefix = Prefix('tq.val.meta', "urn:meta:bim2rdf:TopQuadrantValidation:")
