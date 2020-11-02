from pyprojroot import here
from pathlib import Path
import os
project_root_dir = project_root = root_dir = here(project_files=('.here', 'bootstrap.sh', 'bootstrap.bat'))
project_name = os.environ.get('PROJECT_NAME')
assert(project_name)
del here, Path, os
__all__ = ['root_dir', 'project_root', 'project_root_dir', 'project_name']
