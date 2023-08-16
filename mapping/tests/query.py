# should this be under src? TODO
"""
query testing util.
"""

q = """\
PREFIX spkl: <http://speckle.systems/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX meta: <http://meta>

select ?s ?vl  (count(?f)-1 as ?pos) ?xyz  ?b
where {

?s spkl:category "Lighting Fixtures".
?s spkl:transform/spkl:matrix ?vl.
    # path 'parts' must contain: dispalyValue, vertices, and data
    # connect them in whatever way
    #?m spkl:speckle_type "Objects.Geometry.Mesh".
    #?dc spkl:speckle_type "Speckle.Core.Models.DataChunk".
    #?m  spkl:vertices ?vl.
    #?vl rdf:rest*/rdf:first ?xyz.      # order not guaranteed!
?vl rdf:rest* ?f. ?f rdf:rest* ?n.  # conects (first, next) ptrs to data list
?n rdf:first ?xyz.

#filter(?s =spkl:b355f4bc783e05e4b29bb2482237ca36)

                                                 # b for branch
<<?s spkl:category "Lighting Fixtures" >> meta:  <<?b spkl:name "electrical">>.

}
group by ?b ?s ?vl ?n ?xyz
order by ?vl ?pos
limit 30
"""

q = """\
PREFIX spkl: <http://speckle.systems/>
PREFIX meta: <http://meta>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select  ?s ?vl  (count(?f)-1 as ?pos) ?xyz
where {

?s spkl:category "Lighting Fixtures".
?s spkl:transform/spkl:matrix ?vl.
    # path 'parts' must contain: dispalyValue, vertices, and data
    # connect them in whatever way
    #?m spkl:speckle_type "Objects.Geometry.Mesh".
    #?dc spkl:speckle_type "Speckle.Core.Models.DataChunk".
    #?m  spkl:vertices ?vl.
    #?vl rdf:rest*/rdf:first ?xyz.  # order not guaranteed!
    ?vl rdf:rest* ?f. ?f rdf:rest* ?n. # conects (first, next) ptrs to data list
    ?n rdf:first ?xyz.

# tricky!
<<?n rdf:first ?xyz >> meta: <<?branch spkl:name "electrical" >>.
<<?s spkl:category "Lighting Fixtures" >> meta: <<?branch spkl:name "electrical" >>.

}
group by ?s ?vl ?n ?xyz
order by ?vl ?pos
"""


def query(q, ttl):
    ...


if __name__ == '__main__':
    import sys
    from pyoxigraph import Store
    g = Store()
    from pathlib import Path
    ttl = Path(sys.argv[1])
    assert(ttl.exists())
    g.bulk_load(open(ttl), 'text/turtle')
    _ = g.query(q)
    import pandas as pd
    _ = pd.DataFrame(
            tuple(
                tuple(c.value
                    for c in qs)
                for qs in _),
            columns=[v.value for v in _.variables])
    with pd.option_context(
        'display.max_rows', None,
        'display.max_columns', None):
        print(_)

