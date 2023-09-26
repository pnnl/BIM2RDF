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

space =  "<http://speckle.systems/92aae4513016cb4b2509abc87002e040>"
door = "<http://speckle.systems/e9d5acacef9c1f5919023ab01085711b>"

oo =    "<http://speckle.systems/5110826a766e8bd2f6a1cecf6de2a69f>"
inlight = "<http://speckle.systems/5b9b49428464c68d85e431a937ae964b>"
outlight = "<http://speckle.systems/133bf1ff08bb6bbdd516a25cd8f81d3f>"


branch = 'architecture/rooms and lighting fixtures'
ol = geo.Object(outlight, db._store, branch=branch)
il = geo.Object(inlight, db._store, branch=branch)
o2 = geo.Object(oo, db._store, branch=branch)


print('start')
start = time()
print(
ol in o2, il in o2,
)

for c in geo.compare(db._store, 'Spaces', 'Rooms', branch, branch, analysis='fracInside'):
   print(c.o1.uri, c.fracInside, c.o2.uri)
   print(c.triples())
   break


print(time()-start)