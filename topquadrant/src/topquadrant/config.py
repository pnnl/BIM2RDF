def config():
    from .install import check_java
    check_java()
    from .install import ShaclInstallation
    ShaclInstallation()


if __name__ == '__main__':
    from fire import Fire
    Fire(config)
