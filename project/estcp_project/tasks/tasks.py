from invoke import task, Collection
from estcp_project import root
import yaml
from .. import work
from pathlib import Path


ns = Collection()


# SETUP tasks
setup_coll = Collection('setup')

@task
def set_dvc_repo(ctx, dir=r"E:\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo"):
    """
    Set sharefolder as (non- source code) DVC repository.
    """
    dir = Path(dir)
    if not dir.is_dir():
        raise FileNotFoundError('not a directory or directory not found')

    dir = dir.absolute()
    ctx.run(f"dvc remote add sharefolder \"{dir}\" -f")
    ctx.run(f"dvc config core.remote sharefolder")
setup_coll.add_task(set_dvc_repo)


@task
def create_secrets(ctx):
    """
    Set up secrets config.
    """
    import estcp_project.config
    def input_secrets(): # in tasks
        ret = {}
        ret['mdms'] = {}
        ret['mdms']['user'] = input('mdms user: ')
        ret['mdms']['password'] = input('mdms password: ')
        return ret
    estcp_project.config.save_secrets(input_secrets)
setup_coll.add_task(create_secrets)

#@task(, default=True)
#def setup(ctx, ):
#     """All setup tasks"""
#     pass
# setup_coll.add_task(setup)

ns.add_collection(setup_coll)

dir_help = 'directory relative to project directory'
@task(help={'dir': dir_help})
def create_WorkDir(ctx, dir):
    """
    Initializes a work dir with special files.
    """
    dir = Path(dir)
    if len(dir.parts) > 1:
        print('keep work directories flat')
        exit(1)
    wd = work.WorkDir(dir)
    return wd

@task
def list_work_dirs(ctx):
    """Lists work directories"""
    for wd in work.find_WorkDirs():
        print(wd.name)
ns.add_task(list_work_dirs)

def get_current_conda_env():
    import os
    dir = Path(os.getenv('CONDA_PREFIX')) # can't rely conda info active env
    if not dir:
        return
    else:
        return dir.parts[-1]

def get_current_work_dir():
    import os
    _ = Path(os.curdir).absolute()
    _ = _.relative_to(root)
    if len(_.parts) == 0:
        return
    else:
        if _.parts[0] in (wd.name for wd in work.find_WorkDirs()):
            return _.parts[0]
        else:
            return

def get_current_WorkDir():
    wd = get_current_work_dir()
    if wd:
        return work.WorkDir(wd)
    return

@task
def make_dev_env(ctx, work_dir=get_current_work_dir(),  recreate=False):
    """
    Create conda development environment.
    """
    if not work_dir:
        print('No work directory. Create one.')
        exit(1)
    wd = work.WorkDir(work_dir)
    
    if recreate:
        try:
            (wd.dir / 'environment.yml').unlink()
        except FileNotFoundError:
            pass
        ctx.run(f'conda env remove -n {wd.devenv_name}')

    if 'base' != get_current_conda_env():
        print("Create dev environment from 'base' environment:")
        print("> conda activate base")
        print(f"> cd { work_dir } (the work dir)")
        print("> conda devenv")
        print("Then come back with: conda activate estcp-project.")
        exit(1)
    #with ctx.cd(str(wd.dir.absolute())): doesn't work
    #devenv = wd.dir / 'environment.devenv.yml'
    #devenv = devenv.absolute()
    #conda_base = (Path(str(
    #conda_base = ctx.run('conda info --base', hide='out').stdout.replace('\n','')
    #conda_base = (Path(conda_base) / 'Scripts' / 'conda')
    #breakpoint()
    #ctx.run(f'conda devenv --file "{devenv}"', env={'PATH': str(conda_base) })


ns.add_task(make_dev_env)

@task(help={'dir': dir_help})
def work_on(ctx, work_dir):
    """
    Instructs what to do to work on something.
    Keep invoking until desired state achieved.
    """
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        wd = create_WorkDir(ctx, wd)
    else:
        wd = work.WorkDir(wd)

    #                                           sometimes nonzero exit returned :/
    envlist = ctx.run('conda env list', hide='out', warn=True).stdout
    # checking if env created for the workdir
    if envlist.count(wd.devenv_name+'\n') != 1:
        make_dev_env(ctx, work_dir=wd.name)
        if wd.minrunenv == yaml.safe_load(open(wd.dir/'environment.run.yml')):
            print('Created minimal dev env. Modify environment.[devenv|run].yml as needed and make dev env')

    env_name = get_current_conda_env()
    if wd.devenv_name != env_name:
        print(f'Activate environment: conda activate {wd.devenv_name}')
        exit(1)

    if wd.dir.resolve() != Path('.').resolve():
        rdir = ['..']*wd.n_upto_proj() + [wd.name]
        rdir = Path(*rdir)
        print(f"Change directory to {rdir}")
        exit(1)
    
    print('Ready to work!')
ns.add_task(work_on)



# task: reset/clean env

# run dvc conda run


# clean env

# git commit [tags]
# ok just do setup.py programmatically