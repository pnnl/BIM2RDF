


def config(dev = True):
    from project.tasks.git import config as gitconfig
    if dev: gitconfig(dev=dev)
    from speckle.config import config;          config(dev=dev)
    from project_azure.config import config;    config(dev=dev)
    from project_dvc.config import config;      config(dev=dev)
    from mapping.config import config;          config(dev=dev)
    from topquadrant.config import config;      config()
    #from graphdb.graphdb import config; config(dev=dev)
    # from <workspace>.config import config; config()
    # ...etc.
    # order might matter
    ...


if __name__ == '__main__':
    import fire
    fire.Fire(config)
