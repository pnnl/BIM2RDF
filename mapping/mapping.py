

#%%
def get_obda():
    from jinja2 import Environment, FileSystemLoader#, select_autoescape
    env = Environment(loader=FileSystemLoader('.'))
    import yaml
    mapping = yaml.safe_load(open('mapping.yaml'))

    def strip_comments(lines):
        lines = lines.split('\n')
        o = ""
        for ln in lines:
            o += ln.split('#', 1)[0]
            o += ' ' # need a lil space sometimes
        return o
    for map in mapping['maps']:
        map['target'] = strip_comments(map['target'])
        map['source'] = strip_comments(map['source'])
    return env.get_template('obda.jinja').render(**mapping)

def sqlmap(onto='ontology', fn='mapped'):
    from pathlib import Path
    from shutil import which
    ontop = Path(which('ontop')).absolute()
    from subprocess import run
    # ontop materialize ^
    # --properties sqldb.properties ^
    # -m mapping.obda ^
    # -t Brick.ttl ^
    # --disable-reasoning ^
    # -f turtle ^
    # -o mapping
    o = Path('.') / f'{fn}.ttl'
    m = Path('.') / 'mapping.obda'
    assert(m.exists())
    onto = Path('.') / f'{onto}.ttl' if not onto.endswith('.ttl') else onto
    assert(onto.exists())
    p = Path('.') / 'sqldb.properties'
    assert(p.exists())
    if o.exists():
        o.unlink()
    import yaml
    r = run([
        ontop, 'materialize',
        '--properties', str(p),
        '-m', str(m),
        '-t', str(onto),
        '--disable-reasoning',
        '-f', 'turtle',
        '-o', fn,
        '--db-password', 'sdfsdffsd' 
    ], cwd=Path('.'),
    shell=False, check=True, 
    )
    assert(o.exists())
    return o


def do():
    from graph import get_223p, export
    import rdflib
    b = get_223p()
    m = rdflib.Graph().parse('mapping.ttl')
    # TODO fig out importing graphs
    #for p,u in tuple(m.namespaces()): doesnt work. ontop complians
    #    if 'qudt' in str(u): m.parse(u)
    o = b+m
    export(o, 'ontology')
    from mapping import get_obda
    open('mapping.obda', 'w').write(get_obda())
    m = sqlmap('ontology')
    m = rdflib.Graph().parse(m)
    g = m+o
    return export(g)


if __name__ == '__main__':
    do()
