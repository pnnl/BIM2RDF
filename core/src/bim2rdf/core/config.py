# dev mode config
envvar_prefix='BIM2RDF'
from dynaconf import Dynaconf
config = Dynaconf(
    environments=False,  #  top-level [default] [dev] ...
    merge_enabled=True,
    settings_files=['config.toml', '.secrets.toml', '.config.local.toml' ],
    envvar_prefix = envvar_prefix,    
    load_dotenv=True,
)

# have to consolidate here
def spkl():
    from bim2rdf.speckle.config import defaults
    config.setdefault('speckle', {})
    config.speckle.setdefault('server', defaults.server)
spkl()

config.speckle.setdefault('automate', {})


if __name__ == '__main__':
    # print the config
    from sys import argv
    _ = argv[1]
    _ = config[_]
    print(_)
