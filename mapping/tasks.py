from invoke import task
from ontologies import get


@task
def get_ontologies(ctx):
    from ontologies import init
    init()



@task
def clean(what):
    pass