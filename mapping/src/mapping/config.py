

def download_og_server(ver='0.3.22', ):
    from platform import system
    system = system().lower()
    from urllib.request import urlopen
    if 'windows' in system:
        url = f"https://github.com/oxigraph/oxigraph/releases/download/v{ver}/oxigraph_server_v{ver}_x86_64_windows_msvc.exe"
    elif 'darwin' in system:
        url = f"https://github.com/oxigraph/oxigraph/releases/download/v{ver}/oxigraph_server_v{ver}_x86_64_apple"
    else:
        assert('linux' in system)
        url = f"https://github.com/oxigraph/oxigraph/releases/download/v{ver}/oxigraph_server_v{ver}_x86_64_linux_gnu"

    from project import root
    dd = root / 'mapping' / 'tests' / ('oxigraph_server'+'.exe') if 'windows' in system else ''
    open(dd, 'wb').write(urlopen(url).read() )
    import os
    os.chmod(dd , 0o777)
    


def config(dev=True):
    if dev:
        download_og_server()


if __name__ == '__main__':
    from fire import Fire
    Fire(config)