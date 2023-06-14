from pathlib import Path
import os
try:
    from pyprojroot import here
    project_root_dir = project_root = root_dir = here(project_files=('.here', 'bootstrap.sh', 'bootstrap.bat'))
    del here
except:
    project_root_dir = project_root = root_dir = Path(os.environ.get('PROJECT_ROOT'))
    
work_dir = os.environ.get('WORKDIR')
assert(work_dir)
activated_work_dir = activated_workdir = project_root / work_dir

def _get_current_work_dir():
    import os
    _ = Path(os.curdir).absolute()
    _ = _.relative_to(project_root_dir)
    if len(_.parts) == 0:
        return
    else:
        #if _.parts[0] in (wd.name for wd in work.find_WorkDirs()):
        #    return _.parts[0]
        return _.parts[0]
        #else:
            #return
cur_work_dir = _get_current_work_dir()
cur_work_dir = (project_root / cur_work_dir ) if cur_work_dir else None
current_workdir = current_work_dir = curr_workdir = curr_work_dir = cur_workdir =  cur_work_dir
project_name = os.environ.get('PROJECT_NAME')
assert(project_name)
del Path, os, work_dir
__all__ = [
    'root_dir', 'project_root', 'project_root_dir',
    'project_name' ,
    'current_workdir', 'current_work_dir', 'curr_workdir', 'cur_workdir', 'cur_work_dir',
    'activated_work_dir', 'activated_workdir',]
