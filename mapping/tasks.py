from invoke import task


@task
def get_ontologies(ctx):
    from ontologies import init
    init()


from pathlib import Path
from project import activated_workdir


@task
def map(ctx,
        ontology, map_file = None,
        building=None, 
        db_file=str(activated_workdir / 'work' /'db.sqlite'),
        ):
    import mapping.mapping as m
    # db
    db_file = Path(db_file)
    if not db_file.exists(): raise FileNotFoundError('db file doesnt exist')
    db_file = m.SQLiteDB(db_file)
    # bdg
    if not building: building = db_file.stem
    #             Building | Any,
    #             Ontology | Any,
    #             SQLRDFMap | Any,
    #             SQLiteDB | Any,
    sr = m.SQLRDFMapping.make((building, ontology, map_file, db_file))
    sr.map(db_file.parent)

