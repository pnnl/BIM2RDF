import marimo

__generated_with = "0.8.3"
app = marimo.App(width="full")


@app.cell
def __():
    import dvcdiff.files as ddf
    g = ddf.Get('../models/params.yaml',
    reva='d5f2a590cd26ce854b60d24ed4c1faa69878ab39', 
    revb='bda2c9e89ba7c0256311bff1d44556cc0223a48c',
    )
    ddf.Diff(g).lines().b == ddf.Diff(g).lines().a
    return ddf, g


@app.cell
def __():
    from dvc.api import DVCFileSystem as FS
    a = FS(rev='d5f2a590cd26ce854b60d24ed4c1faa69878ab39').open('../models/params.yaml', ).read().decode()
    a
    return FS, a


@app.cell
def __(FS):
    b = FS(rev='bda2c9e89ba7c0256311bff1d44556cc0223a48c').open('../models/params.yaml', ).read().decode()
    b
    return b,


@app.cell
def __():

    #                         modified:           run.variation
    # ..\models\dvc.yaml:report:
    #         changed deps:
    #                 modified:           ..\models\db
    #                 ..\models\params.yaml:
    #                         modified:           run.building
    #                         modified:           run.variation
    return


@app.cell
def __(a, b):
    a == b
    return


if __name__ == "__main__":
    app.run()
