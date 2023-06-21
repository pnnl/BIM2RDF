
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
