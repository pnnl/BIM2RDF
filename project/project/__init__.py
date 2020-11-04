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
project_name = os.environ.get('PROJECT_NAME')
assert(project_name)
del Path, os, work_dir
__all__ = [
    'root_dir', 'project_root', 'project_root_dir',
    'project_name' ,
    'activated_work_dir', 'activated_workdir',]
