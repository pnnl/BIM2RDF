


def config(dev = True):
    from .git import config as gitconfig
    if dev: gitconfig()
    # TODO: trigger configs from each workspace.
    # from <workspace>.config import config; config()
    # ...etc.
    # order might matter
    ...


if __name__ == '__main__':
    import fire
    fire.Fire(config)
