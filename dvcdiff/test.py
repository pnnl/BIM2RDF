import marimo

__generated_with = "0.8.3"
app = marimo.App(width="full")


@app.cell
def __():
    import dvcdiff.files as ddf
    ddf.diff('../models/params.yaml',
    reva='d5f2a590cd26ce854b60d24ed4c1faa69878ab39', 
    revb='bda2c9e89ba7c0256311bff1d44556cc0223a48c',
    )
    return ddf,


if __name__ == "__main__":
    app.run()
