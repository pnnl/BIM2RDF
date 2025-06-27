from bim2rdf.core.queries import SPARQLQuery
class ValidationQuery:
    def __init__(self, q: SPARQLQuery|str) -> None:
        if isinstance(q, str):
            q = SPARQLQuery(q)
        else:
            assert(isinstance(q, SPARQLQuery))
        self.q = q
        self.msg = self.extract_msg(str(q))
    from functools import cache, cached_property

    def __str__(self) -> str:
        return str(self.q)
    
    @classmethod
    def extract_msg(cls, s: str):
        _ = s
        _ = s.split('\n')
        _ = (m for m in _ if 'message:' in m)
        _ = (m[m.find(':')+1:] for m in _)
        _ = ' '.join(_)
        return _
    @classmethod
    def extract_tgt(cls, s: str):
        p = r'\?this\s+a\s+(\w+:\w+)'
        _ = s
        from re import search
        match = search(p, _)
        if match:
            return match.group(1)
        else:
            return None
    
    @cached_property
    def type(self):
        s = {'AskQuery', 'SelectQuery'}
        _ = self.algebra().name
        assert(_ in s)
        return _
    
    @cache
    def algebra(self):
        from rdflib.plugins.sparql.processor import prepareQuery
        _ = str(self)
        _ = prepareQuery(_)
        _ = _.algebra
        return _
    
    @cache
    def parse(self):
        from rdflib.plugins.sparql import parser
        q = str(self.q)
        _ = parser.parseQuery(q).asList(flatten=True)
        return _

    @cached_property
    def prefixes(self):
        from bim2rdf.core.rdf import Prefix
        return [Prefix(name=i['prefix'], prefix=i['iri'])
                 for i in self.parse() if 'prefix' in i]
    
    def shacl(self, msg='') -> str:
        q = self.q
        q = ValidationQuery(q)
        if q.type != 'SelectQuery':
            raise NotImplementedError('validation query type not implemented')
        q = str(q)
        if not msg: msg = str(q)
        from bim2rdf.core.queries import SPARQLQuery
        prefixes = SPARQLQuery.defaults.prefixes
        assert(prefixes)
        def declare(n, u):
            _ = f"""sh:declare [
                sh:prefix    \"{n}\";
                sh:namespace <{u}>;
            ]
            """
            return _
        prefixes = map(lambda i: declare(i[0], i[1]), prefixes.items())
        prefixes = ';\n'.join(prefixes)
        query_prefixes = SPARQLQuery.defaults.substitutions['query.prefixes']
        # sh:targetClass  rdfs:Resource; # 'wildcard' doesnt work. i wish it did.
        # dynamic target (w/ query) https://www.w3.org/TR/shacl12-sparql/#example-dynamically-computed-target-nodes-using-a-node-expression-based-on-a-sparql-query
        # sh:
        s = f"""{query_prefixes}
        _:s a sh:NodeShape;
            sh:targetClass {self.extract_tgt(q)};
            sh:sparql [
                a sh:SPARQLConstraint;
                sh:message \"""{self.msg}\""";
                sh:prefixes _:p;
                sh:select \""" {q} \"""
        ].
        _:p {prefixes} .
        """
        from rdflib import Graph
        s = Graph().parse(data=s, format='turtle')
        s = s.serialize(format='turtle')
        return s

