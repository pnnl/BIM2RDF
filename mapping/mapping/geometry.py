from typing import Tuple, Iterable

Point = Tuple[float, float, float]
def point_inside_points(
        pt:             Point,
        pts: Iterable[  Point ]) \
    -> bool:
    """inside ...or touching"""
    if len(pts) < 2:
        raise ValueError('need at least to pts to make sense')
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

