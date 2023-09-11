


def config(dev = True):
    from project.tasks.git import config as gitconfig
    if dev: gitconfig(dev=dev)
    from speckle.config import config; config(dev=dev)
    from speckle.graphql import client;client(dev=dev)
    from speckle.requests import get_session; get_session(dev=dev)
    from project_azure.config import config; config(dev=dev)
    #from graphdb.graphdb import config; config(dev=dev)
    # TODO: trigger configs from each workspace.
    # from <workspace>.config import config; config()
    # ...etc.
    # order might matter
    ...


if __name__ == '__main__':
    import fire
    fire.Fire(config)
