from invoke import task


@task
def get_ontologies(ctx):
    from ontologies import init
    init()


from pathlib import Path



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

