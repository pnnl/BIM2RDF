


def config(dev = True):
    from project.tasks.git import config as gitconfig
    if dev: gitconfig(dev=dev)


if __name__ == '__main__':
    import fire
    fire.Fire(config)
