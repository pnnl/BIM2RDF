1. [Develop mappings](../mapping/README.md).
2. Run `bim2rdf --help`.
   Inspect results by querying [oxigraph server](https://github.com/oxigraph/oxigraph/releases).
   Use `python -m bim2rdf.queries query` to extract graph data.
3. Regression test with (verbose) `pytest -vvv -s`.
   First run will always fail. Run again.
   Regression test query results show up in the [test directory](./test/).
4. Goto 1.
