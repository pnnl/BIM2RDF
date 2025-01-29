from ..rule import Rule
class Query(str): ...
class TopQuadrant(Rule):
    from bim2rdf.rdf import Prefix
    meta_prefix = Prefix('tq.meta', "urn:meta:bim2rdf:TopQuadrant:")
    def __init__(self, *, data: Query, shapes: Query):
        assert('construct' in data.lower())
        assert('construct' in shapes.lower())
        data =   Query(data)
        shapes = Query(shapes)
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
        from pytqshacl import infer
        inputs = self.prep(db)
        _ = infer(inputs.dp, shapes=inputs.sp)
        inputs.dp.unlink()
        inputs.sp.unlink()
        from pyoxigraph import parse, RdfFormat
        breakpoint()
        _ =  parse(_.stdout, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        yield from _
        