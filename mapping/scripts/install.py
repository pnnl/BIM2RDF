from project import activated_workdir

ontop_loc = activated_workdir / 'ontop-cli'

def download_ontop(ver = '4.2.0'):
    url = f"https://github.com/ontop/ontop/releases/download/ontop-{ver}/ontop-cli-{ver}.zip"
    dst = activated_workdir/ 'ontop-cli.zip'

    if not dst.exists():
        print('downloading ontop cli')
        from urllib.request import urlretrieve
        urlretrieve(url, dst)

    from zipfile import ZipFile
    ZipFile(dst).extractall(ontop_loc)
    dst.unlink()



def download_sqlite_driver(ver='3.36.0.3'):
    fn = f"sqlite-jdbc-{ver}.jar"
    url = f"https://github.com/xerial/sqlite-jdbc/releases/download/{ver}/{fn}"
    dst = ontop_loc / 'jdbc' / fn
    
    if not dst.exists():
        print('dowloading sqlite driver')
        from urllib.request import urlretrieve
        urlretrieve(url, dst)
    


download_ontop()
download_sqlite_driver()
