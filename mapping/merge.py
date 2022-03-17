from subprocess import run as _run
import os

def run(*a, check=True, shell=True, **k):
    return _run(*a, check=check, shell=shell, **k)

import mapping as m


from pathlib import Path


m.sqlmap()
mapped = Path('./mapped.ttl').absolute()
assert(mapped.exists())


mods = Path('./mapping.ttl').absolute()
assert(mods.exists())


os.chdir('tasty')
run('git checkout nrel-pnnl')
run('git pull --autostash')

import rdflib
mdg = rdflib.Graph().parse(mods)
mpg = rdflib.Graph().parse(mapped)

mrg = Path('.') / Path('examples/nrel_pnnl/pnnl/mediumOffice_brick.ttl')
mrg = mrg.absolute()
(mdg+mpg).serialize(str(mrg), format='turtle')



# run(f'git add {merged}')
# run(f'git commit -m "merge test"')
# run('git push')
