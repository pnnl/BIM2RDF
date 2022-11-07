from invoke import task, Collection

ns = Collection()
ns.add_collection(Collection('graphdb'))

@task
def get_ontologies(ctx):
    from ontologies import init
    init()
ns.add_task(get_ontologies)

from pathlib import Path

repo = 'pnnl'

@task 
def update_repo(ctx):
    config={
        'rep:repositoryID': repo}
    from graphdb.graphdb import repo_config,  bot_user, get_bot_password
    from graphdb.api import workbench_base
    import requests
    ids = {_['id'] for _ in requests.get(f"{workbench_base}/repositories", auth=(bot_user, get_bot_password() ) ).json()}

    def args():
        from getpass import getpass
        return (
                (f"{workbench_base}/repositories",),
                {   'auth':(input('user: '), getpass('password: ') ) ,  # auth=(bot_user, bot_password), manual
                    'files':[('config', repo_config(config).serialize(format='turtle')) ],})
    if config['rep:repositoryID'] not in ids:
        p, k = args()
        _ = getattr(requests, 'post')(*p, **k)
        assert(_.ok)
    else:
        raise NotImplementedError('repo update case')
        p, k = args()
        _ = getattr(requests, 'post')(*p, **k) # should be put??
        assert(_.ok)
ns.collections['graphdb'].add_task(update_repo)


@task
def upload_graph(ctx, ttl, name=None):
    from pathlib import Path
    ttl = Path(ttl)
    assert(ttl.exists())
    if not name: name = ttl.stem
    from graphdb.api import rdf4j_base
    from graphdb.graphdb import repo_config,  bot_user, get_bot_password
    import requests
    breakpoint()
    _ = requests.post(
        f"{rdf4j_base}/{repo}/rdf-graphs/{name}",
        auth=(bot_user, get_bot_password()),
        headers={"Content-Type": 'text/turtle'},
        data=(open(ttl, 'rb').read().decode()) )
    #assert(_.status_code == 200)
    assert(_.ok)

ns.collections['graphdb'].add_task(upload_graph)


def init(): #TODO
    ...
    # getontos and create_repo

    
    
@task
def map(ctx,
        ontology, map_file = None, # (Path.cwd() / 'maps.yaml' ),
        building=None, 
        db_file= (Path.cwd() /'db.sqlite'),
        work_dir = Path.cwd()
        ):
    # copy input files to workdir
    from shutil import copy2 as copy
    

    import mapping.mapping as m
    # db
    db_file = Path(db_file)
    if not db_file.exists(): raise FileNotFoundError('db file doesnt exist')
    if db_file.parent != work_dir:
        db_file = Path(copy(db_file, work_dir))
    db_file = m.SQLiteDB(db_file)

    # bdg
    if not building: building = db_file.stem

    # map
    if map_file:
        map_file = Path(map_file)
        if not map_file.exists(): raise FileNotFoundError('map file doesnt exist')
        if map_file.parent != work_dir:
            map_file = Path(copy(map_file, work_dir))

        map_file = m.SQLRDFMap.make(map_file)
    #             Building | Any,
    #             Ontology | Any,
    #             SQLRDFMap | Any,
    #             SQLiteDB | Any,

    

    sr = m.SQLRDFMapping.make((building, ontology, map_file, db_file))
    sr.map(work_dir)
ns.add_task(map)
