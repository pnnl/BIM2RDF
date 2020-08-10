from pathlib import Path
from pyprojroot import here # 0.1.2
import yaml


class WorkDir():
    # TODO: probably better managed as a tree
    file_names = {'environment.devenv.yml',
                  }
                  # could also be some configs
    base_devenv = here('./environment.yml')
    envfn = 'environment.yml'

    def __init__(self, dir: Path):
        self.dir = here() / Path(dir)
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
            if p.samefile(here().absolute()):
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
        if name == 'self.devenv_name':
            name = self.devenv_name
        from pathlib import PurePosixPath as P
        include_work_dirs = list(include_work_dirs)
        include_work_dirs = include_work_dirs + ['project'] if 'project' not in include_work_dirs else include_work_dirs
        includes = [ str(P("{{root}}") / P("..") / P(inc).stem/ 'environment.devenv.yml' ) for inc in include_work_dirs]
        dev_env = {
            'includes': includes,
            'name': name,
            'dependencies':[],
            'environment': {
                'PATH':       ['{{root}}/wbin', '{{root}}'],
                'PYTHONPATH': [                 '{{root}}'],
            }
        }
        return dev_env

    def make_devenv_file(self, *args, **kwargs):
        dev_env = self.make_devenv(*args, **kwargs)
        with open(self.dir / 'environment.devenv.yml', 'w') as ef:
            yaml.dump(dev_env, ef)
        ef.close()
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
    for dir in here().glob('**/'):
        if WorkDir.is_work_dir(dir):
            yield WorkDir(dir)
