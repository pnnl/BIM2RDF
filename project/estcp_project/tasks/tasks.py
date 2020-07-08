from invoke import task, Collection, call
from estcp_project import root
import yaml
from .. import work
from pathlib import Path


ns = Collection()



# SETUP tasks
setup_coll = Collection('setup')
ns.add_collection(setup_coll)

@task
def set_dvc_repo(ctx,
                prompt=True,
                dir=r"\\pnl\projects\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo"):
    """
    Set sharefolder as (non- source code) DVC repository.
    """
    if prompt:
        if input(f"Enter 'Y' if {dir} is the DVC repo. ").lower() == 'y':
            pass
        else:
            dir = input("input DVC repo: ")

    dir = Path(dir).resolve().absolute()
    if not dir.is_dir():
        raise FileNotFoundError('not a directory or directory not found')
    ctx.run(f"dvc config --local core.remote sharefolder")
    ctx.run(f"dvc remote add --local sharefolder \"{dir}\" -f")
    sdvc = root / 'data' / 'sample.dvc'
    # will not error if file in (local) cache but wrong remote
    ctx.run(f"dvc pull \"{root/'data'/'sample.dvc'}\"")
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


def copy_git_hook_file(name):
    src = root /  'git' / 'hooks' / name
    dst = root / '.git' / 'hooks' / name
    src = open(src, 'r').read()
    open(dst, 'w').write(src)
    # +x flag set in git. so the following isn't needed
    #from stat import S_IXUSR
    #dst.chmod(S_IXUSR)

@task
def create_project_git_commit_hook(ctx):
    """
    Set up git commit automation which prepends commits with [<workdir>]
    """
    copy_git_hook_file('prepare-commit-msg')
setup_coll.add_task(create_project_git_commit_hook)


@task
def create_dvc_git_hooks(ctx):
    # luckily it doesn't conflict with project git commit hook
    """
    Set up dvc git hooks.
    """
    copy_git_hook_file('post-checkout')
    copy_git_hook_file('pre-commit')
    copy_git_hook_file('pre-push')
setup_coll.add_task(create_dvc_git_hooks)


@task
def create_project_wrappers(ctx, ):
    """
    Create wrappers around project tool executables.
    """
    #for #dvc, git, invoke, work-on.sh/enter: bash --login -i
    for exe in ['dvc', 'invoke', 'inv',]+['git', 'bash']:
        create_exec_wrapper(ctx, exe_name=exe, work_dir='project')
setup_coll.add_task(create_project_wrappers)



@task(
    pre=[
        create_secrets,
        create_project_git_commit_hook,
        create_dvc_git_hooks,
        create_project_wrappers,
        call(set_dvc_repo, prompt=True)],
    default=True)
def setup(ctx,):
     """All setup tasks"""
     pass
setup_coll.add_task(setup)

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


def _create_WorkDir(ctx, dir):
    """
    Initializes a work dir with special files.
    """
    dir = Path(dir)
    if len(dir.parts) > 1:
        print('keep work directories flat')
    wd = work.WorkDir(dir)
    return wd

@task
def list_work_dirs(ctx):
    """Lists work directories"""
    for wd in work.find_WorkDirs():
        print(wd.name)
ns.add_task(list_work_dirs)

cur_work_dir = get_current_work_dir()
def get_cur_work_dir_help():
    cd = ''
    if cur_work_dir:
        cd += f" Default: {cur_work_dir}"
    return f"Work directory."+cd


@task(help={
    'exe_name': "name of executable",
    'test': "test if executable can be seen before making a wrapper around it"
    })
def create_exec_wrapper(ctx, exe_name='_stub',  work_dir=cur_work_dir, test=True): #TODO: create script arg?
    """
    Create wrapper around executable in work dir env.
    """
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    wd = work.WorkDir(root / work_dir)
    env_pth = wd.get_env_path()
    if not env_pth:
        raise Exception('no associated environment')
    
    def create_wrapper(exe_name, test=True):
        from shutil import which
        if not test:
            # overwrites
            # just fills in a name
            ctx.run(f"create-wrappers -t conda -f {exe_name} -d \"{wd.dir/'wbin'}\" --conda-env-dir \"{env_pth}\"")
            return Path(which(exe_name, path=f"{wd.dir/'wbin'}"))  # Path doesn't work until py3.8
        
        wpth = create_wrapper(exe_name, test=False) # stub
        wtxt = open(wpth).read()
        assert(wpth.exists())
        wpth.unlink() #missing_ok=False) # py38 thing. wpth must exist
        # so now the following doesn't pick up the wrapped exe. breaks out of recursion issues.
        get_exe_py = f"from shutil import which; print(which(\'{exe_name}\'))"
        exe = ctx.run(f"{wd.dir/'wbin'/'run-in'} python -c \"{get_exe_py}\"", hide='out').stdout.replace('\n', '')
        if exe=='None': raise Exception(f'{exe_name} exe not found')

        # create wrappers uses colon, :,  to separate -f exec. windows problem. so using $exe to sub in
        _ = wtxt.replace(exe_name, f"{Path(exe).absolute()}")
        open(wpth, 'w').write(_)
        return wpth
        
    if exe_name == '_stub':
        return create_wrapper(exe_name, test=False)
    wpth = create_wrapper(exe_name, test=True)
    from shutil import copy2 as copyexe # attempt to copy all metadata (mainly keeping +x attrib)
    from shutil import which
    assert(wpth.stem == exe_name)
    env_exec_pth = wpth.parent / f"{exe_name}-{wd.name}{wpth.suffix}"
    copyexe(wpth, env_exec_pth)
    run_in_pth = which('run-in', path=str(wpth.parent))
    assert(run_in_pth)
    run_in_pth = Path(run_in_pth)
    assert(run_in_pth.exists())
    copyexe(run_in_pth, run_in_pth.parent / f"{run_in_pth.stem}-{wd.name}{run_in_pth.suffix}")
    print(f"created wrapper {wpth} for {exe_name}")
    print(f"created wrapper {env_exec_pth} for {exe_name}")
    return wpth
ns.add_task(create_exec_wrapper)



def create_scripts_wrappers(ctx, work_dir=cur_work_dir):
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    wd = work.WorkDir(root / work_dir)
    sdir = wd / 'scripts'


def _make_dev_env(work_dir=cur_work_dir, ):
    # TODO use conda run base devenv
    """
    Create conda development environment.
    """
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    
    #if recreate:
    #    try:
    #        (wd.dir / 'environment.yml').unlink()
    #    except FileNotFoundError:
    #        pass
    #    remove_work_env(work_dir)

    # expecting this condition almost always
    print("Create dev environment from 'base' environment:")
    print("> conda activate base")
    _change_dir(wd)
    print(f"Modify environment.run.yml and environment.devenv.yml as needed.")
    print("> conda devenv")


def _change_dir(wd):
    if wd.dir.resolve() != Path('.').resolve():
        n_up = len(Path('.').absolute().parts) - len(wd.dir.absolute().parts) + 1
        assert( (n_up-1) !=0)
        if n_up>0:
            deeper = True
            rdir = ['..']*n_up + [wd.name]
            rdir = Path(*rdir)
        else:
            deeper = False
            rdir = Path(wd.dir).absolute().relative_to(Path('.').absolute())
        print(f"Change directory to {rdir}.")
        print(f"> cd {rdir}")
        return True
    else:
        return None

# TODO create recreate env task


@task(help={'work_dir': "directory to work on something"})
def work_on(ctx, work_dir, ): # TODO rename work_on_check ?
    """
    Instructs what to do to work on something.
    Keep invoking until desired state achieved.
    """
    cur_branch = ctx.run('git rev-parse --abbrev-ref HEAD', hide='out').stdout.replace('\n','')
    cur_env_name = get_current_conda_env()

    def init_commit(wd):
        ctx.run(f'git add "{wd.dir}"')
        ctx.run(f'git commit -m  " [{wd.name}]  initial placeholder commit"')

    # best programmed with a state diagram. TODO 


    # 1. check work dir creation
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        # best to do this from the project env 
        # b/c the git hook prepends WORK_DIR
        project_env = work.WorkDir(root/'project').devenv_name  # hardcoding warning
        if cur_env_name !=  project_env:
            print("Change to project environment before creating a new workdir.")
            print(f"> conda activate {project_env}")
            exit(1)
        # state of just creating a workdir
        if cur_branch != 'master':
            if input(f"Current git branch is not 'master'. Enter 'Y' if  you're sure that you want to initialize the work dir in the '{cur_branch}' branch.").lower() == 'y':
                wd = _create_WorkDir(ctx, wd)
                init_commit(wd)
            else:
                print('Switch to master.')
                print('> git checkout master')
                exit(1)
        else:
            wd = _create_WorkDir(ctx, wd)
            init_commit(wd)
    else:
        wd = work.WorkDir(wd)
    
    # 2. check env creation
    #                                           sometimes nonzero exit returned :/
    envlist = ctx.run('conda env list', hide='out', warn=True).stdout
    # checking if env created for the workdir
    if envlist.count(wd.devenv_name+'\n') != 1:
        _make_dev_env(work_dir=wd.name)
        exit(1)
    
    # 3. did you try ?
    minRunenv = \
        wd.minrunenv \
        == yaml.safe_load(open(wd.dir/'environment.run.yml'))
    minDevenv = \
        yaml.safe_load(open(wd.dir/'environment.devenv.yml')) \
        == wd.make_devenv()
    #            'or' instead of 'and' since the intent is to get the user to do /something/.
    if (minRunenv or minDevenv):
        print('Minimal dev or run env detected.')
        _make_dev_env(work_dir=wd.name)
        # but no exit(1)
    
    # 4. create wrapper scripts
    #TODO: craete script wrappers
    create_exec_wrapper(ctx, exe_name='_stub', work_dir=wd.name)
    

    # check if devenv in run env includes. TODO

    # 5. check if in env
    if wd.devenv_name != cur_env_name:
        print(f'Activate environment:')
        print(f'> conda activate {wd.devenv_name}')
        exit(1)

    # 6. check if in dir
    if _change_dir(wd):
        exit(1)

    # 7. check if in a branch
    if ('master' == cur_branch) and (wd.name != 'project'):
        print('Notice: You many want to create a branch for your work.')
    
    print('Ready to work!')
# TODO check WORK_DIR set
ns.add_task(work_on)

# TODO: recreate is this followed by a workon
@task(help={'work-dir': get_cur_work_dir_help() })
def remove_work_env(ctx, work_dir=cur_work_dir):
    """
    Removes conda environment associated with work dir.
    """
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        print('Work dir not found.')
        exit(1)
    wd = work.WorkDir(wd)
    #                                           sometimes nonzero exit returned :/
    envlist = ctx.run('conda env list', hide='out', warn=True).stdout
    # checking if env created for the workdir
    if envlist.count(wd.devenv_name+'\n') != 1:
        print("No env associated with work dir.")
        exit(0)
    else:
        if wd.devenv_name == get_current_conda_env():
            if wd.devenv_name == 'estcp-project':
                print("Don't remove base/project env.")
            else:
                print("Can't remove current env. Go to another env:")
                print("> conda activate estcp-project")
            exit(1)
        else:
            #(wd.dir / wd.envfn).unlink(missing_ok=True) py3.8
            envfn = (wd.dir / wd.envfn)
            if envfn.exists():
                envfn.unlink()
            print(f"> conda env remove -n {wd.devenv_name}")
ns.add_task(remove_work_env)

# @task(help={'message': "Commit message. Use quotes.",
#             'work-dir': get_cur_work_dir_help() })
# def commit(ctx, message, work_dir=cur_work_dir):
#     """
#     Prefixes commit message with workdir.
#     """
#     wd = work_dir
#     if wd not in (wd.name for wd in work.find_WorkDirs()):
#         print('Work dir not found.')
#         exit(1)
#     wd = work.WorkDir(wd)

#     message = f"[{wd.name}] " + message
#     ctx.run(f"git commit  -m  \"{message}\"")
# ns.add_task(commit)




# todo: use WORK_DIR instead of conda env where applicable
#check_state(cd = workdir and workdir env var)
#@task TODO
def dvc_run(ctx,  work_dir=cur_work_dir):
    """
    Executes .dvc files.
    """
    ...
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        print('Work dir not found.')
        exit(1)
    wd = work.WorkDir(wd)
    work_on(ctx, wd.dir)
#ns.add_task(dvc_run)

# run dvc conda run
# task: reset/clean env
# clean env
# TODO feature: optionally print out shell cmds.

# ok just do setup.py programmatically

# 
_coll = Collection('_')
ns.add_collection(_coll)

@task
def prepare_commit_msg_hook(ctx,  COMMIT_MSG_FILE): # could not use work_dir
    """
    (ignore. internal task.) git commit hook for workdir tag
    Uses WORK_DIR env var to prefix commit msg.
    """
    import os
    WORK_DIR = os.environ.get('WORK_DIR') # COULD USE cd ??
    if WORK_DIR:
        wd = work.WorkDir(WORK_DIR)
        message = f"[{wd.name}] " + open(COMMIT_MSG_FILE, 'r').read()
        cmf = open(COMMIT_MSG_FILE, 'w')
        cmf.write(message)
        cmf.close()
    else:
        print('No WORK_DIR environment variable.')
        exit(1)
_coll.add_task(prepare_commit_msg_hook)
