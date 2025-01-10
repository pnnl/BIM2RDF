# dev mode config

envvar_prefix='B2R'
from dynaconf import Dynaconf
config = Dynaconf(
    environments=False,  #  top-level [default] [dev] ...
    settings_files=['config.toml', '.secrets.toml'],
    envvar_prefix = envvar_prefix,    
    load_dotenv=True,
)

def spkl():
    from speckle.config import defaults
    config.setdefault('speckle', {})
    config.speckle.setdefault('server', defaults.server)
spkl()


if __name__ == '__main__':
    # print the config
    from sys import argv
    _ = argv[1]
    _ = config[_]
    print(_)
