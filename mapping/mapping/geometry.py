from typing import Tuple, Iterable

Point = Tuple[float, float, float]
def is_point_inside_points(
        pt:             Point,
        pts: Iterable[  Point ]) \
    -> bool:
    """inside ...or touching"""
    if len(pts) < 2:
        raise ValueError('need at least two pts to make sense')
    mnx = min(p[0] for p in pts)
    mny = min(p[1] for p in pts)
    mnz = min(p[2] for p in pts)
    mxx = max(p[0] for p in pts)
    mxy = max(p[1] for p in pts)
    mxz = max(p[2] for p in pts)
    cond = [
        (mnx <= pt[0] <= mxx),
        (mny <= pt[1] <= mxy),
        (mnz <= pt[2] <= mxz),]
    if all(cond):
        return True
    else:
        return False


def list_to_pts(l):
    l = list(l)
    assert(not len(l) % 3)
    # take every 3rd
    xs = (l)[0::3]
    ys = (l)[1::3]
    zs = (l)[2::3]
    _ = zip(xs, ys, zs)
    _ = list(_)
    return _


def test():
    def qp(r): print(*r,sep='\n')

    import speckle.graphql as sg
    import speckle.objects as o
    d=sg.query(sg.queries().objects)
    g=o.rdf(d)
    qr = g.query("""
    PREFIX spkl: <http://speckle.systems/>
    select ?m  ?v
        where {
            ?m spkl:speckle_type "Objects.Geometry.Mesh".
            ?m spkl:vertices/spkl:data ?v. 
            spkl:cd987c37645ab9e185590d290c3d5223 spkl:speckle_type "Speckle.Core.Models.DataChunk".
        }
    """)
    _=qr
    qp(qr)
    return _
    qr=g.query("""
      PREFIX spkl: <http://speckle.systems/>
      select ?p ?x ?y ?z
        where {
        ?p spkl:category "Lighting Fixtures". # filter
        ?p spkl:basePoint/spkl:x ?x.
        ?p spkl:basePoint/spkl:y ?y.
        ?p spkl:basePoint/spkl:z ?z.
        }
    """)
    _ = qr
    return _
