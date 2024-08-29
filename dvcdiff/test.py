import marimo

__generated_with = "0.8.3"
app = marimo.App(width="full")


@app.cell
def __():
    import dvcdiff.files as ddf
    ddf.Get('../models/params.yaml').pth
    return ddf,


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


if __name__ == "__main__":
    app.run()
