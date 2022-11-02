from invoke import task


@task
def get_ontologies(ctx):
    from ontologies import init
    init()


from pathlib import Path


@task  # TODO create graphdb task ns
def update_repo(ctx):
    config={
        'rep:repositoryID': "pnnl"}
    from graphdb.graphdb import repo_config, host, bot_user, bot_password
    import requests
    ids = {_['id'] for _ in requests.get(f"{host}/rest/repositories", auth=(bot_user, bot_password ) ).json()}

    def args():
        from getpass import getpass
        return (
                (f"{host}/rest/repositories",),
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

