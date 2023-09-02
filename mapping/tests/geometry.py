import mapping.speckle as m
from pyoxigraph import Store
from pathlib import Path
td = Path('tmp')
if not td.exists():
    s = Store('tmp')
    s.bulk_load('../work/out.ttl', 'text/turtle')
else:
    s = Store('tmp')

db = m.OxiGraph(s)
#e = m.Engine(g)
#e = e()

import mapping.geometry as geo
from time import time
roof = "<http://speckle.systems/f19e851bf8b35a971bb8d48021cee5aa>"
chair = "<http://speckle.systems/a3bcdc5c0ee2e46689f256c6b43fe798>"
light = "<http://speckle.systems/0786c943cd6bc8164bd3e61946d779a9>"
space =  "<http://speckle.systems/92aae4513016cb4b2509abc87002e040>"
door = "<http://speckle.systems/e9d5acacef9c1f5919023ab01085711b>"
branch = 'architecture/rooms and lighting fixtures'
o1 = geo.Object(light, db._store, branch=branch)
o2 = geo.Object(chair, db._store, branch=branch)

print('start')
start = time()
for c in geo.compare(db._store, 'Lighting Fixtures', 'Rooms', branch, branch):
    print('c')
    print(c,)
#o1s = list(geo.Object.get_objects(db._store, 'Lighting Fixtures', branch))
#print('o1s')
#o2s = list(geo.Object.get_objects(db._store, 'Rooms', branch))
#print('o2s')
#print(o1s[0].vertices())
#o1s = list(o1s)
print(time()-start)
# g = geo.get_geometry(db._store,
#              o, 'Lighting Fixtures', 'vertices',
#             branch='architecture/rooms and lighting fixtures')

#os = geo.get_objects(db._store, 'Lighting Fixtures', branch='architecture/rooms and lighting fixtures')
#_ = geo.has_property(db._store, 'Lighting Fixtures', 'xdisplayValue')
#_ = geo.has_property(db._store, 'definition', subject=o)
#print('property:', _)
breakpoint()
