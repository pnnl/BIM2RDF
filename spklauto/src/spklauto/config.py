envvar_prefix='SPECKLE'
from dynaconf import Dynaconf
config = Dynaconf(
    environments=False,  #  top-level [default] [dev] ...
    settings_files=['config.toml', '.secrets.toml'],
    envvar_prefix = envvar_prefix,    
    load_dotenv=True,
)

#locals().update(**config)  make a problem in test! idk!

if __name__ == '__main__':
    # print the config
    from sys import argv
    _ = argv[1]
    _ = config[_]
    print(_)
