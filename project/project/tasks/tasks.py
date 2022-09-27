from invoke import task, Collection
from .. import project_root_dir, project_name, cur_work_dir
cur_work_dir = cur_work_dir.name if cur_work_dir else None
import yaml
from .. import work
from pathlib import Path

# need a var called ns!!!
ns = coll = collection = Collection()
# PROJECT
coll.add_collection(Collection('project'))
coll.collections['project'].add_collection(Collection('setup'))
coll.collections['project'].add_collection(Collection('action'))
coll.collections['project'].add_collection(Collection('info'))


# WORK DIR
coll.add_collection(Collection('work-dir'))
coll.collections['work-dir'].add_collection(Collection('setup'))
coll.collections['work-dir'].add_collection(Collection('action'))
coll.collections['work-dir'].add_collection(Collection('info'))


config = yaml.safe_load((project_root_dir / 'project' / 'config.yml').open())



def get_cur_work_dir_help():
    cd = ''
    if cur_work_dir:
        cd += f" Default: {cur_work_dir}"
    return f"Work directory."+cd


@task(
    help={
        'work-dir': "directory to work in a workdir",
        'prompt-setup': 'prompt setup tasks',
        'skip_setup': "skips executing setup scripts (effectively just installs dependencies)"})
def work_on(ctx,
        work_dir=cur_work_dir, skip_project_workdir=False,
        skip_setup=False, prompt_setup=False, ): # TODO rename work_on_check ?
    """
    >> Sets up an existing or new work dir.
    """
    cur_branch = ctx.run('git rev-parse --abbrev-ref HEAD', hide='out').stdout.replace('\n','')
    cur_env_name = get_current_conda_env()

    def init_commit(wd):
        ctx.run(f"conda run -n {work.WorkDir('project').devenv_name} git add {wd.dir}", echo=True)
        ctx.run(f"conda run -n {work.WorkDir('project').devenv_name} git commit -m  \"initial placeholder commit\"", echo=True)

    # best programmed with a state diagram. TODO

    # 1. check work dir creation
    if ' ' in work_dir:
        raise ValueError(f"Work directory, {work_dir}, has spaces. Create work directory w/o spaces.")
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        new_work_dir = True
        # best to do this from the project env
        project_env = work.WorkDir(project_root_dir/'project').devenv_name
        if cur_env_name !=  project_env:
            print("Change to project environment before creating a new workdir.")
            print(f"> conda activate {work.WorkDir(project_root_dir/'project').devenv_name}")
            exit(1)
        # state of just creating a workdir
        # if cur_branch != 'master':
        #     if input(f"Current git branch is not 'master'. Enter 'Y' if  you're sure that you want to initialize the work dir in the '{cur_branch}' branch.").lower() == 'y':
        #         wd = _create_WorkDir(ctx, wd)
        #         init_commit(wd)
        #     else:
        #         print('Switch to master.')
        #         print('> git checkout master')
        #         exit(1)
        #else:
        wd = _create_WorkDir(ctx, wd)
        #init_commit(wd)

    else:
        new_work_dir = False
        wd = work.WorkDir(wd)

    # 2. env yml creation
    minDevenv = \
       (open(wd.dir/'environment.devenv.yml')).read() \
       == wd.make_env()
    if minDevenv:
       print('Minimal env detected. Make sure that this is intended.')

    # 3 install deps (libs) .. but dont execute setup tasks
    build(ctx, work_dir)


    # 4. run setup tasks
    if not skip_setup:
        run_setup_tasks(ctx, work_dir=work_dir, prompt=prompt_setup, skip_project_workdir=skip_project_workdir)

    # check if devenv in run env includes. TODO

    # 6. check if in env
    #if wd.devenv_name != cur_env_name:
    #    print(f'Activate environment:')
    #    print(f'> conda activate {wd.devenv_name}')
    #    exit(1)

    # 7. check if in dir
    #if _change_dir(wd):
    #    exit(1)

    # 8. check if in a branch
    if cur_branch in {'master', 'main'}:
        print('Note: You many want to create a branch for your work.')

    print('Ready to work!')
    print(f'Activate environment:')
    print(f'> conda activate {wd.devenv_name}')
coll.collections['work-dir'].collections['setup'].add_task(work_on)
coll.add_task(work_on)


@task
def create_project_wrappers(ctx, ):
    """
    Create wrappers around project tool executables.
    """
    for exe in ['git', 'bash', 'pre-commit',]:
        create_exec_wrapper(ctx, exe, work_dir='project')
coll.collections['project'].collections['setup'].add_task(create_project_wrappers)


@task
def set_git_hooks(ctx):
    """
    install git hooks using pre-commit tool
    """
    def inform_hookfile(hf):
        #https://github.com/pre-commit/pre-commit/issues/1329
        from shutil import which
        exe_pth = work.WorkDir('project').dir / 'wbin' / Path(which('project-python')).name
        uninformed_line = "INSTALL_PYTHON ="
        informed_line = f"INSTALL_PYTHON = \"{Path(exe_pth)}\""
        informed_line = informed_line.encode('unicode-escape').decode() + "\n"
        _ = open(hf).readlines()
        assert(''.join(_).count(uninformed_line) == 1)
        lines = []
        for al in _:
            if uninformed_line in al:
                al = informed_line
            lines.append(al)
        open(hf, 'w').writelines(lines)

    if config['git']:
        ctx.run(f"pre-commit install", echo=True)
        # make the stupid pre-commit exec invocation see the pre-commit exec instead of a python
        inform_hookfile(project_root_dir / '.git' / 'hooks' / 'pre-commit', )
        ctx.run(f"pre-commit install    --hook-type     prepare-commit-msg", echo=True)
        inform_hookfile(project_root_dir / '.git' / 'hooks' / 'prepare-commit-msg')
    else:
        ctx.run(f"pre-commit uninstall", echo=True)
        ctx.run(f"pre-commit uninstall    --hook-type     prepare-commit-msg", echo=True)
coll.collections['project'].collections['setup'].add_task(set_git_hooks)


@task(default=True)
def setup(ctx,):
    """All setup tasks"""
    if ' ' in str(project_root_dir):
        raise ValueError(f"Project directory: {project_root_dir} has spaces. Move to location w/o spaces.")
    print('creating scripts wrappers')
    create_scripts_wrappers(ctx, work_dir='project')
    print('creating project wrappers')
    create_project_wrappers(ctx)
    print('setting git hooks')
    set_git_hooks(ctx)
    #run_setup_tasks(ctx, work_dir='project') inf loop
    #make_devenv(ctx, work_dir='project') # doesn't make sense
coll.collections['project'].collections['setup'].add_task(setup)


def get_current_conda_env():
    import os
    dir = Path(os.getenv('CONDA_PREFIX')) # can't rely conda info active env
    if not dir:
        return
    else:
        return dir.parts[-1]


@task
def project_root(ctx):
    print(project_root_dir)
coll.collections['project'].collections['info'].add_task(project_root)



@task
def work_dir_list(ctx):
    """Lists work directories"""
    for wd in work.find_WorkDirs():
        print(wd.name)
coll.collections['project'].collections['info'].add_task(work_dir_list)


def _get_current_work_dir():
    from . import cur_work_dir
    return cur_work_dir.name if cur_work_dir else None


@task
def current_work_dir(ctx):
    cd = _get_current_work_dir()
    if cd: print(cd)
    else: exit(1)
coll.collections['work-dir'].collections['info'].add_task(current_work_dir)



def get_current_WorkDir():
    wd = _get_current_work_dir()
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


def _get_workdir_deps(ctx, WD, reversed=False):
    return [wdn for wdn in ctx.run(f"deps -p {WD.dir} {'--deps-reversed' if reversed else ''}", hide='out').stdout.split('\n') if wdn]


@task(help={'work-dir':get_cur_work_dir_help()})
def work_dir_work_dir_deps(ctx, work_dir=cur_work_dir, reversed=False):
    """
    lists work dir dependencies of work dir
    """
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    for wdn in _get_workdir_deps(ctx, work.WorkDir(work_dir), reversed=reversed):
        print(wdn)
coll.collections['work-dir'].collections['info'].add_task(work_dir_work_dir_deps)


@task(help={'work-dir': get_cur_work_dir_help()})
def work_dir_deps(ctx, work_dir=cur_work_dir, pattern='.*'):
    work_dirs = _get_workdir_deps(ctx, work.WorkDir(work_dir))
    assert(work_dir in work_dirs)
    devfile_deps = {wd: _get_work_dir_deps(wd, pattern) for wd in work_dirs}
    # merging
    deps = set()
    pip_deps = set()
    for wd in devfile_deps:
        for dep in devfile_deps[wd]:
            if isinstance(dep, str): deps.add(dep)
            else:
                for pipdep in dep['pip']:
                    pip_deps.add(pipdep)
    deps = list(deps)
    if pip_deps: deps.append({'pip': list(pip_deps)})
    import json
    print(json.dumps(deps))
coll.collections['work-dir'].collections['info'].add_task(work_dir_deps)


def _get_work_dir_deps(work_dir, pattern):
    pattern = f".*\[{pattern}\]"
    # not comfortable with thie util. it gets into conda devenv's biz

    # need the deps defined in the devenv file
    _ = project_root_dir / work_dir / 'environment.devenv.yml'
    _ = open(_)
    #from jinja2 import Environment, BaseLoader
    #import yaml
    #_ = Environment(loader=BaseLoader()).from_string(_.read())
    #_ = _.render()
    #_ = yaml.safe_load(_)
    #_ = _['dependencies']
    # not a clean way to do this
    _ = _.readlines()
    for i, l in enumerate(_):
        if l.startswith('dependencies:'):
            break
    _ = _[i+1:]
    for i, l in enumerate(_):
        if not l.strip().startswith('-') and l[0].isalpha():
            break
    # deps section lines
    _ = _[:i]
    # remove lines that dont look like items
    _ = [l for l in _ if l.strip().startswith('-')]
    from re import match
    _ = [l for l in _ if match(pattern, l) or match(r'\s*-\s*pip:', l)]
    devfile_deps = yaml.safe_load(''.join(_)) if _ else []
    del l

    def has(deps, sec='pip'):
        for i, d in enumerate(deps):
            if isinstance(d, dict):
                if sec in d:
                    return True, i
        return False, None

    def normalize(dep):
        m = match("([a-z0-9\-\_]+)(.*)", dep)
        name = m[1]
        ver =  m[2]
        return ''.join((name, ver))

    if has(devfile_deps, 'pip')[0]:
        pip_deps = devfile_deps[has(devfile_deps, 'pip')[1]]['pip']
        pip_deps = pip_deps if pip_deps else []
        devfile_deps.pop(has(devfile_deps, 'pip')[1])
    else:
        pip_deps = []
    from re import match
    pip_deps =   [normalize(d) for d in pip_deps     ]
    conda_deps = [normalize(d) for d in devfile_deps ]

    devfile_deps = conda_deps
    if pip_deps:
        devfile_deps.append({'pip': pip_deps})
    return devfile_deps



@task(help={'work-dir': get_cur_work_dir_help()})
def work_dir_deps_tree(ctx, work_dir=cur_work_dir, all_dirs=False):
    """
    print dependency tree of work dir
    """
    if all_dirs:
        work_dirs = (wd for wd in work.find_WorkDirs())
    else:
        if work_dir not in (wd.name for wd in work.find_WorkDirs()):
            print('work dir not found')
            exit(1)
        work_dirs = [work.WorkDir(work_dir), ]
    
    cmd = f"deps -pp "
    for wd in work_dirs: cmd += f"-p {wd.dir} "
    ctx.run(cmd, echo=False)
coll.collections['project'].collections['info'].add_task(work_dir_deps_tree)



@task(help={
    'exe': "name or path of executable",
    'test': "test if executable can be seen before making a wrapper around it"
    })
def create_exec_wrapper(ctx, exe='_stub',  work_dir=cur_work_dir, test=True): #TODO: create script arg?
    """
    Create wrapper around executable in work dir env.
    """
    exe_pth = Path(exe)
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found.')
        exit(1)
    wd = work.WorkDir(project_root_dir / work_dir)
    env_pth = wd.get_env_path()
    if not env_pth:
        raise Exception('no associated environment')

    exe_name = exe_pth.stem

    def create_wrapper(exe_pth, test=True): # TODO rename exp_pth > exe_pth_or_name
        exe_pth = Path(exe_pth)
        exe_name = exe_pth.stem
        exe_prefix_switch = f"-b {exe_pth.parent}" if exe_pth.parent.parts else ''
        from shutil import which
        if not test:
            # overwrites
            ctx.run(f"create-wrappers -t conda {exe_prefix_switch} -f {exe_name} -d {wd.dir/'wbin'} --conda-env-dir {env_pth}", echo=True)
            w = Path(which(exe_name, path=str(wd.dir/'wbin')))  # Path doesn't work until py3.8
            import stat
            w.chmod(w.stat().st_mode | stat.S_IEXEC) # do i have to do this?
            return w

        if not exe_pth.parent.parts:
            get_exe_py = f"from shutil import which; print(which(\'{exe_name}\'))"
            exe_pth = ctx.run(f"{wd.dir/'wbin'/'run-in'} python -c \"{get_exe_py}\"", hide='out').stdout.replace('\n', '')
            if exe_pth=='None': raise Exception(f'{exe_name} exe not found')
        else:
            exe_pth = Path(exe_pth).absolute()
            if not exe_pth.exists():
                raise Exception(f'{exe_pth} does not exist')
        return create_wrapper(exe_pth, test=False)

    if exe_name == '_stub':
        wpth = create_wrapper(exe_name, test=False)
        wpth.unlink()
        wpth, env_exec_pth = create_exec_wrapper(ctx, '_prefixed-stub', work_dir=work_dir, test=False)
        wpth.unlink()
        env_exec_pth.unlink()
        return wpth, env_exec_pth
    # so now the following doesn't pick up the wrapped exe. breaks out of recursion issues.
    create_wrapper(exe_pth, test=False).unlink()
    wpth = create_wrapper(exe_pth, test=test)
    def copyexe(src, dst, ):
        def make_executable(path):
            from os import stat, chmod
            mode = stat(path).st_mode
            mode |= (mode & 0o444) >> 2    # copy R bits to X
            chmod(path, mode)
        from shutil import copy
        if Path(dst).exists(): Path(dst).unlink()
        copy(src, dst)
        make_executable(dst)
    from shutil import which
    assert(wpth.stem == exe_name)
    env_exec_pth = wpth.parent / f"{wd.name}-{exe_name}{wpth.suffix}"
    copyexe(wpth, env_exec_pth)
    run_in_pth = which('run-in', path=str(wpth.parent))
    assert(run_in_pth)
    run_in_pth = Path(run_in_pth)
    assert(run_in_pth.exists())
    # creating {name prefix}-run-in
    copyexe(run_in_pth, run_in_pth.parent / f"{wd.name}-{run_in_pth.stem}{run_in_pth.suffix}")
    print(f"created wrapper {wpth} for {exe_name}")
    print(f"created wrapper {env_exec_pth} for {exe_name}")
    return wpth, env_exec_pth
coll.collections['work-dir'].collections['action'].add_task(create_exec_wrapper)


@task
def create_scripts_wrappers(ctx, work_dir=cur_work_dir):
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    wd = work.WorkDir(project_root_dir / work_dir)
    sdir = wd.dir / 'scripts'
    assert(sdir.exists())
    (sdir / 'bin').mkdir(exist_ok=True)

    def _make_cmd_lines(cmds, type, ):
        # assuming simple case: just lines of cmds
        if isinstance(cmds, str):
            cmds = [cmds]
        cmds = [cmd.strip() for cmd in cmds]
        lines = []
        al = lambda ln: lines.append(ln)

        if type=='bat':
            al('@echo off')
            al('setlocal')
            for i, cmd in enumerate(cmds):
                if not cmd.replace(' ', ''): continue
                al(f"call {cmd} || goto:error")
            al("goto:EOF")
            al(":error")
            al(r"exit /b %errorlevel%")
            al('endlocal')
        
        elif type=='sh':
            al("#!/bin/sh")
            al('set -e')
            for i, cmd in enumerate(cmds):
                if not cmd.replace(' ', ''): continue
                # pass args to 1st cmd
                al(f"{cmd}")
        
        else:
            raise NotImplementedError(f"{type}")

        return tuple(lines)

    def replace_args(ln, tgt): # copypaste to test
        from re import findall, match
        digits = "[0-9]+"
        argpattern = f"(\${{{digits}}})"
        for m in findall(argpattern, ln):
            i = int(match( f"\${{({digits})}}" , m).groups()[0])
            if tgt=='bat':
                ln = ln.replace(m,  f"%{i}")
            else:
                assert(tgt=='sh')
                ln = ln.replace(m,  f"${i}")
        argpattern = "\${\*}"
        m = findall(argpattern, ln)
        if m:
            assert(len(m)==1)
            m = m[0]
            if tgt=='bat':
                ln = ln.replace(m, r"%*")
            else:
                assert(tgt=='sh')
                ln = ln.replace(m, "$@")
        return ln

    def subs_envvars(lines):
        lines = [
                     ln.replace("${WORK_DIR}",      str(wd.name))
                       .replace("${WORKDIR}",       str(wd.name))
                       .replace("${WORK_DIR_PATH}", str(wd.dir ))
                       .replace("${WORKDIR_PATH}",  str(wd.dir ))
                       .replace("${PROJECT_ROOT}",  str(project_root_dir   ))
                       .replace("${PROJECTROOT}",   str(project_root_dir   ))
                       # TODO:     get these from workdir env os.getenv. defined in environment.devenv.template.yml
                for ln in lines
                if not ln.startswith('#')
                ]
        return lines

    def process_cmdlines(cmds, type):
        cmds = subs_envvars(cmds)
        cmds = [replace_args(ln, type) for ln in cmds]
        cmds = _make_cmd_lines(cmds, type)
        return cmds


    def chmod_px(pth):
        import stat
        return pth.chmod(pth.stat().st_mode | stat.S_IEXEC)

    def write_sbin(sbin, lines):
        lines = [ln.strip()+'\n' for  ln in lines]
        open(sbin, 'w', ).writelines(lines)
        chmod_px(sbin)
        return sbin
    def write_nsbin(sbin, lines):
        sbin0 = sbin; del sbin
        sbin0 = write_sbin(sbin0, lines)
        sbin1 = sbin0.with_name(f"self-{sbin0.name}")
        sbin1 = write_sbin(sbin1, lines)
        return (sbin0, sbin1)

    # .r, .sh, .py, .bat., .
    for script_pth in sdir.glob('*'):
        if script_pth.is_dir(): continue
        name = script_pth.stem
        ext = script_pth.suffix[1:] if script_pth.suffix else None
        sbin_bat =  sdir / 'bin' / f"{name}.bat"
        sbin_sh =   sdir / 'bin' / f"{name}.sh"
        sbin_cmd =  sdir / 'bin' / f"{name}.cmd"
        sbin_name = sdir / 'bin' / name
        from platform import system as platform
        platform = platform().lower()
        if 'windows' in platform:
            sbin = sbin_bat
        else:
            sbin = sbin_name

        def create_wrappers(sbin, lines):
            sbins = write_nsbin(sbin, lines)
            sbin = sbins[0]
            assert('self-' not in str(sbin))
            wpths = create_exec_wrapper(ctx, sbin,  work_dir=work_dir, test=True)
        def create_cmdlines_wrappers(sbin, lines):
            if sbin == sbin_bat:
                lines = process_cmdlines(lines, 'bat')
            else:
                lines = process_cmdlines(lines, 'sh')
            create_wrappers(sbin, lines)
        
        if ext == 'cmdlines':
            lines = open(script_pth).readlines()
            #lines = ["cd ${WORK_DIR_PATH}"]+lines
            create_cmdlines_wrappers(sbin, lines)

        elif ext == 'py':
            # prep
            lines = ["cd ${WORK_DIR_PATH}", f"python {script_pth.absolute()} ${{*}}",]
            create_cmdlines_wrappers(sbin, lines)

        elif ext == 'bat':
            lines = ["cd ${WORK_DIR_PATH}", f"{script_pth.absolute()} ${{*}}",]
            create_cmdlines_wrappers(sbin, lines)
            print('make sure to include corresponding .sh script.')

        elif ext == 'sh':
            lines = ["cd ${WORK_DIR_PATH}", f"sh {script_pth.absolute()} ${{*}}",]
            create_cmdlines_wrappers(sbin, lines)
            print('make sure to include corresponding .bat script.')
        
        else:
            print(f'{script_pth} processing not implemented.')
coll.collections['work-dir'].collections['action'].add_task(create_scripts_wrappers)

@task
def build(ctx, work_dir=cur_work_dir, prompt=False, skip_project_workdir=False, reversed=False):
    """
    execute all installation tasks for the workdir (plus workdirs that depend on it)
    """
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    import os
    # have to render the devenv first
    dep_work_dirs = _get_workdir_deps(ctx, wd, reversed=reversed)
    assert(dep_work_dirs) # should have at least project
    done = []
    for dwd in dep_work_dirs:
        if dwd in done: continue # possibly deduping
        if work_dir != 'project' and dwd == 'project' and skip_project_workdir:
            print('INFO: (re)-building project skipped.')
            continue
        # 1. make the dev env
        if prompt:
            if input(f"create ({dwd}) env? [enter y for yes] ").lower().strip() == 'y':
               other_deps = make_env(ctx, work_dir=dwd)
        else:
            other_deps = make_env(    ctx, work_dir=dwd)
        dWD = work.WorkDir(dwd)
        done.append(dWD.name)
    #ctx.run(f"conda run --cwd {wd.dir} -n {wd.env name} conda devenv", echo=True) # pyt=True does't work on windows
coll.collections['work-dir'].collections['setup'].add_task(build)

@task
def make_env(ctx, work_dir=cur_work_dir):
    """
    Create only specified (one) conda  environment.
    """
    # my mamba use issue https://github.com/ESSS/conda-devenv/issues/109
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    # asserts maybe aren't necessary b/c warn=False default
    # idk why this failure didnt exit nonzero!!
    import os
    import pathlib
    prefix = pathlib.Path(os.environ['CONDA_PREFIX']).parent / wd.devenv_name
    def delete_condadevenvactivation(): 
        p = prefix / 'etc' / 'conda' 
        _ = p / 'activate.d' 
        _ = list(_.glob('devenv-vars*'))
        if _: _[0].unlink(); 
        _ = p / 'deactivate.d' 
        _ = list(_.glob('devenv-vars*'))
        if _: _[0].unlink()
#delete_condadevenvactivation()

    with ctx.cd(str(wd.dir)):
        print('The devenv is:')
        devenv = ctx.run("conda devenv --print-full", echo=False).stdout
        import yaml
        devenv = yaml.safe_load(devenv)
        en =    devenv['name']
        from subprocess import run as sprun
        existing_envs = sprun('conda env list --json', shell=True, text=True, capture_output=True)
        import json
        existing_envs = json.loads(existing_envs.stdout)['envs']
        import pathlib
        #existing_envs = frozenset(pathlib.Path(e).name for e in existing_envs)
        #if en not in existing_envs:
        _ = wd.dir / '_.devenv.yml' # https://github.com/ESSS/conda-devenv/issues/90
        with open(_, 'w') as f: yaml.dump(
            {
            'channels': devenv['channels'],
            'name': en,
            'dependencies': ['curl'], # 'stub' dep just to create the env
            'environment': devenv['environment'], # conda has 'variables' instead of environment
                }, f) 
        ctx.run(f"conda devenv  --file {_}", echo=True) # --file doesnt work. this or conda create new if it doesnt exist
        _.unlink()
        (wd.dir / '_.yml' ).unlink()

        if 'channels' in devenv:
            channels =  devenv['channels']
            channelss = '-c ' + ' -c '.join(channels)
        else:
            channelss = ''

        deps =  devenv['dependencies']
        depss = ' '.join('"'+d.replace(' ', '')+'"' for d in deps if isinstance(d, str)) #for pip:installable
        other_deps = []
        for d in deps:
            if not isinstance(d, str):
                other_deps.append(d)
        # https://github.com/ESSS/conda-devenv/issues/126
        try:
            ctx.run(f"mamba install --yes --name {en} {channelss} {depss}", echo=True)
            pass
        except:
            #raise Exception('sort of error. must mamba.')
            print('WARNING: sort of error. didnt mamba.')
            # for the remaining stuff even if mamba installed
            ctx.run(f"conda install --yes --name {en} {channelss} {depss}", echo=True)
        create_exec_wrapper(ctx, '_stub', work_dir=work_dir, test=False) # 
        create_scripts_wrappers(ctx, work_dir=work_dir)
        install_other_deps(ctx, wd, other_deps)
coll.collections['work-dir'].collections['setup'].add_task(make_env)


def install_other_deps(ctx, WD, other_deps):
    # 3. install 'other deps'
    WD = work.WorkDir(WD) if isinstance(WD, str) else WD
    if WD.name != 'project':
        dep_pre = f"{WD.dir / 'wbin' / 'run-in' }"
    else:
        # as an exception, use unwrapped exec when dealing with the 'project' env
        # might create a problem if this program is executed from a wrapper
        dep_pre = f"{WD.dir / 'scripts' / 'bin' / 'run-in'}"
    
    with ctx.cd(str(WD.dir)):
        for od in other_deps:
            assert(isinstance(od, dict))
            installer = list(od.keys())[0]
            specs = od[installer]
            if installer == 'pip':
                # why does conda devnv mess with this??
                pkgs = [p.replace(' ', '') for p in specs]
                # use conda run or wrapper?
                #ctx.run(f"conda run --live-stream --name {dWD.env_name} ... ", echo=True)
                #                idk  pip on its own doesnt work
                ctx.run(f"{dep_pre} python -m {installer} install  {' '.join(pkgs)}", echo=True)
            elif installer == 'cmd':
                # https://github.com/ESSS/conda-devenv/issues/152
                from re import sub
                for spec in specs:
                    spec = spec.split(' ')
                    spec = list(spec)
                    # replaced "(something unique)exe" -> "exe"
                    spec[0] = sub(r'X.*X', '', spec[0])
                    spec = ' '.join(spec)
                    ctx.run(f"{dep_pre} {spec}", echo=True)
            else:
                raise Exception("unrecognized 'other dep'")


def _get_setup_names(wd):
    return list(sorted({p.stem for p in (wd.dir/'scripts').glob('setup*') }))

@task(
    help={
        #'setup_list': 'the name of the setup script  (can be used multiple times to list)',
        'prompt': 'prompt setup tasks',
        },
    #iterable = ['setup_list']
)
def run_setup_tasks(ctx, work_dir=cur_work_dir, prompt=False, skip_project_workdir=False, reversed=False):
    """
    execute all setup tasks for the workdir (plus workdirs that depend on it)
    """
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    # have to render the devenv first
    dep_work_dirs = _get_workdir_deps(ctx, wd, reversed=reversed)
    assert(dep_work_dirs) # should have at least project
    done = []
    for dwd in dep_work_dirs:
        if dwd in done: continue # possibly deduping
        if work_dir != 'project' and dwd == 'project' and skip_project_workdir:
            print('INFO: (re)-building project skipped.')
            continue

        # 2. make script wrappers
        create_exec_wrapper(    ctx, '_stub', work_dir=dwd)
        def make_wrappers():
            create_scripts_wrappers(ctx,          work_dir=dwd)
        if prompt:
            if input(f"make scripts wrappers for ({dwd})? [enter y for yes]").lower().strip() == 'y':
                make_wrappers()
        else:
            make_wrappers()

        dWD = work.WorkDir(dwd)
        # 3. exec setups
        for asetup in  _get_setup_names(dWD):
            with ctx.cd(str(dWD.dir)):
                if dWD.name != 'project':
                    setup_cmd = f"{dWD.dir / 'wbin' / asetup}"
                else:
                    # as an exception, use unwrapped exec when dealing with the 'project' env
                    # might create a problem if this program is executed from a wrapper
                    setup_cmd = f"{dWD.dir / 'scripts' / 'bin' / asetup}"
                if prompt:
                    if input(f"execute {asetup} for ({dWD.name})? [enter y for yes] ").lower().strip() == 'y':
                        assert(ctx.run(setup_cmd, echo=True).ok)
                else:
                    # asserts may not be needed b/c warn=False
                    assert(    ctx.run(setup_cmd, echo=True).ok)
        done.append(dWD.name)
    #ctx.run(f"conda run --cwd {wd.dir} -n {wd.env name} conda devenv", echo=True) # pyt=True does't work on windows
coll.collections['work-dir'].collections['setup'].add_task(run_setup_tasks)


def _change_dir(wd):
    if wd.dir.resolve() != Path('.').resolve():
        print(f"Change directory to {wd.dir}.")
        print(f"> cd {wd.dir}")
        return True
    else:
        return None

# TODO create recreate env task

@task
def run(ctx, work_dir=cur_work_dir,
        parallel=True,
        glob='run*', exclude_glob=None,
        skip_setup=True,
        dry_run=False):
    """runs run script"""
    if not skip_setup: work_on(ctx, work_dir)
    
    from subprocess import Popen
    wd = work.WorkDir(work_dir)
    deps = (work.WorkDir(_) for _ in _get_workdir_deps(ctx, wd, reversed=False))
    deps = frozenset(deps)
    from itertools import chain
    def finds(glob): return chain.from_iterable((r for r in (wd.dir / 'wbin').glob(glob)) for wd in deps)
    includes = frozenset(finds(glob))
    excludes = finds(exclude_glob) if exclude_glob else frozenset()
    includes = includes - excludes
    
    if dry_run:
        for r in includes: print(str(r))
    else:
        if parallel:
            procs = [Popen(i) for i in includes]
            for p in procs: p.wait()
        else:
            for r in includes: ctx.run(str(r), echo=True)
coll.collections['work-dir'].collections['action'].add_task(run)


@task
def work_on_deps_on(ctx, work_dir, skip_setup=False):
    """set up workdirs that depend on a workdir. """
    deps = set()
    for wd in work.find_WorkDirs():
        wdd = _get_workdir_deps(ctx, wd,)
        if work_dir in wdd: deps.add(wd.name)
    for wdn in deps:
        work_on(ctx, wdn, skip_project_workdir=True, skip_setup=skip_setup)
coll.collections['work-dir'].collections['action'].add_task(work_on_deps_on)


# TODO: recreate is this followed by a workon. 
# not used.# maybe remove b/c resest.py in root
@task(help={
    'work-dir': get_cur_work_dir_help(),
    'hard': 'deletes env dirs (instead of asking conda to (nicely) remove them'})
def reset(ctx, work_dir=cur_work_dir, hard=False):
    """
    Recrecreates enviroments associated with the work dir by 'removing' environments.
    """ #                  hah this wouldn't be possible with a container like docker.
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        print('Work dir not found.')
        exit(1)
    wd = work.WorkDir(wd)
    #                                           sometimes nonzero exit returned :/
    
    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.

        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        import stat
        import os
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise
        
    import json
    all_env_dirs = json.loads(ctx.run('conda info --json', hide='out', warn=True).stdout)['envs_dirs']
    from itertools import chain
    all_env_dirs = (Path(dr) for dr in all_env_dirs)
    all_env_dirs = (dr for dr in all_env_dirs if dr.exists())
    all_env_dirs = (dr.iterdir() for dr in all_env_dirs)
    from itertools import chain
    all_env_dirs = chain.from_iterable(all_env_dirs)
    all_env_dirs = (pth for pth in  all_env_dirs if pth.is_dir())
    all_envs = {Path(ed).stem: ed for ed in all_env_dirs}
    deps = _get_workdir_deps(ctx, wd)
    dep_envs = {work.WorkDir(dwd).devenv_name for dwd in deps}
    rem_envs = set(all_envs).intersection(dep_envs)
    assert(rem_envs)
    project_env_name = work.WorkDir(project_root_dir/'project').devenv_name
    for wdenv in rem_envs:
        if wdenv == project_env_name: continue 
        if hard:
            from shutil import rmtree
            print(f'deleting env dir {all_envs[wdenv]}')
            rmtree(all_envs[wdenv], onerror=onerror)
        else: # 
            ctx.run(f"conda env remove -n {wdenv} --yes", echo=True)
            
    for dep in deps:
        del_wrappers(dep)
        del_envfile(dep)
    work_on(ctx, wd.name)
    print('Deactivate then reactivate your environment.')
coll.collections['work-dir'].collections['setup'].add_task(reset)


def del_wrappers(wd):
    # and rem wrappers
    from shutil import rmtree
    wdir = work.WorkDir(wd).dir
    if        (wdir / 'wbin').exists():
        rmtree(wdir / 'wbin')
    if       ( wdir / 'scripts' / 'bin').exists():
        rmtree(wdir / 'scripts' / 'bin')

def del_envfile(wd):
    wdir = work.WorkDir(wd).dir
    # remove generated env file
    if ( wdir / 'environment.yml').exists():
        (wdir / 'environment.yml').unlink()


# TODO: reset work dir


#
coll.collections['project'].add_collection(Collection('_git'))

@task
def prepare_commit_msg_hook(ctx,  COMMIT_MSG_FILE): # could not use work_dir
    """
    (ignore. internal task.) git commit hook for workdir tag
    Uses takes the first dir part to prepend
    """
    commit_msg_file = project_root_dir / COMMIT_MSG_FILE
    assert(commit_msg_file.exists())
    from re import match
    import git
    repo = git.Repo(project_root_dir)
    work_dirs = []
    for pth in repo.index.diff("HEAD"):
        pth = Path(pth.a_path) # a_path or b_path idk
        if len(pth.parts) == 1: # assume project
            work_dirs.append('project')
        else:
            work_dir = pth.parts[0]
            if work_dir == 'notebooking' and (project_root_dir / pth).exists():
                try:
                    m = match(f"display_name: {project_name}-(.*)-(.*)", open(project_root_dir / pth).read())
                except UnicodeDecodeError:
                    continue
                if m:
                    work_dir = m.groups()[0]
            work_dirs.append(work_dir)
    work_dirs = frozenset(work_dirs)

    def find_tags(txt):
        from re import findall
        return findall("\[([^\[\]]{1,})\]", txt)

    if work_dirs:
        tags = ""
        message = open(commit_msg_file, 'r').read()
        existing_tags = find_tags(message)
        for wd in work_dirs:
            if wd not in existing_tags:
                tags += f"[{wd}]"
        message = f"{tags} " + message
        cmf = open(commit_msg_file, 'w')
        cmf.write(message)
        cmf.close()
coll.collections['project'].collections['_git'].add_task(prepare_commit_msg_hook)
