from .run import run


def config(dev=True, ): 
    if not dev: return

    # merging behavior
    run("git config pull.ff only")

    # fix windows stupidity
    run("git config  core.eol lf")
    run("git config  core.autocrlf input")

    # id
    from project import root
    cf = root / 'project' / 'config.json'
    def updateg(c={}):
        c['git'] = {}
        c['git']['name'] =  input("enter git name: " ).strip()
        c['git']['email'] = input("enter git email: ").strip()
        return c
    import json
    if not cf.exists():
        c = updateg()
        json.dump(c, open(cf, 'w'))
    #if update: dont really need this option
    c = json.load(open(cf))
    run(f'git config --local user.name  "{c["git"]["name"]}"')
    run(f'git config --local user.email "{c["git"]["email"]}"')
    
    # hooks
    run(f"pre-commit install",)
    run(f"pre-commit install    --hook-type     prepare-commit-msg",)


def _prepare_commit_msg_hook(COMMIT_MSG_FILE): # could not use work_dir
    """
    (ignore. internal task.) git commit hook for workdir tag
    Uses takes the first dir part to prepend
    """
    from project import project_root_dir
    from pathlib import Path
    commit_msg_file = project_root_dir / COMMIT_MSG_FILE
    assert(commit_msg_file.exists())
    import git
    repo = git.Repo(project_root_dir)
    work_dirs = []
    for pth in repo.index.diff("HEAD"):
        pth = Path(pth.a_path) # a_path or b_path idk
        if len(pth.parts) == 1: # assume project
            work_dirs.append('project')
        else:
            work_dir = pth.parts[0]
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


if __name__ == "__main__":
    import fire
    _ = (config,
          _prepare_commit_msg_hook) # fire doesn't show the cmd if it starts w/ an underscore
          # ...but it's still accessible.
    _ = {f.__name__: f for f in _}
    fire.Fire(_)
