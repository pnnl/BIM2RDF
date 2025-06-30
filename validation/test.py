import marimo

__generated_with = "0.14.9"
app = marimo.App(width="full")


@app.cell
def _():
    import bim2rdf.validation.validation as v
    return (v,)


@app.cell
def _(v):
    from bim2rdf.validation import included_dir
    sq = included_dir / 'lpd.rq'
    sq = open(sq).read()
    print(
    v.ValidationQuery(sq).shacl()
    )
    return (sq,)


@app.cell
def _():
    from pyoxigraph import Store, QueryResultsFormat
    s = Store('../test/db', )
    return (s,)


@app.cell
def _(s, sq):
    _ = (s.query(sq))
    _vs = _.variables
    _ = [{v.value:i[v].value for v in _vs} for i in _]
    _
    return


if __name__ == "__main__":
    app.run()
