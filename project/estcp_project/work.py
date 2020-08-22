from pathlib import Path
from . import project_root
import yaml


class WorkDir():
    # TODO: probably better managed as a tree
    file_names = {'environment.devenv.yml',
                  }
                  # could also be some configs
    base_devenv = project_root / 'environment.yml'
    envfn = 'environment.yml'

    def __init__(self, dir: Path):
        self.dir = project_root / Path(dir)
        self.name = self.dir.name
        if not self.is_work_dir(self.dir):
            self.create_files()

    def create_files(self):
        self.dir.mkdir(exist_ok=True)

        if not (self.dir / 'environment.devenv.yml').exists():
            self.make_devenv_file()

        if not (self.dir / 'readme.md').exists():
            open(self.dir/ 'readme.md', 'w').write('TODO: write readme\n')

        # wbin and scripts? self.dir.mkdir(exist_ok=True)
        #(self.dir / 'wbin').mkdir(exist_ok=True) this is generated
        (self.dir / 'scripts').mkdir(exist_ok=True)


    def reset(self):
        # rem stuff
        #return WorkDir initialized
        ...

    @property
    def id(self):
        return self.dir

    def n_upto_proj(self, ):
        p = self.dir.absolute()
        n = 0
        for _ in range(len(p.parts)):
            p = p / '..'
            n = n + 1
            if p.samefile(project_root):
                return n
        raise FileNotFoundError


    @property
    def devenv_name(self):
        return 'estcp-'+self.name

    def get_env_path(self): # not sure this is the place to put this. as it has less to do with 'dir'
        from subprocess import check_output
        _ = check_output('conda env list --json', shell=True)
        import json
        _ = json.loads(_)
        _ = _['envs']
        from  pathlib import Path
        for pth in _:
            pth = Path(pth)
            if pth.stem == self.devenv_name:
                return pth
        return None


    def make_devenv(self,
                    name='self.devenv_name',
                    include_work_dirs=[]):
        return open(project_root / 'project'/ 'environment.devenv.template.yml').read()

    def make_devenv_file(self, *args, **kwargs):
        dev_env = self.make_devenv(*args, **kwargs)
        f = open(self.dir / 'environment.devenv.yml', 'w')
        f.write(dev_env)
        f.close()
        return dev_env

    @classmethod
    def is_work_dir(cls, dir: Path):
        dir = Path(dir)
        if not dir.is_dir():
            return False
        if all([(dir/f).is_file() for f in cls.file_names]):
            return True
        return False

    def glob_filter(self, pth: Path):
        pth = Path(pth)
        if (not self.is_work_dir(pth)) or (pth == self.dir):
            return pth

    def walk(self):
        for pth in self.dir.glob('**/*'):
            yield self.glob_filter(pth)

    def get_files(self):
        for pth in self.walk():
            if pth.is_file():
                yield pth

    def get_dvc_files(self):
        for f in self.get_files():
            if f.suffix == '.dvc':
                yield f

    def has_env_file(self):
        if Path(envfn) in self.dir.glob(self.envfn):
            return True
        else:
            return False

def find_WorkDirs():
    for dir in project_root.glob('**/'):
        if WorkDir.is_work_dir(dir):
            yield WorkDir(dir)
