





def query(browser=False):
    from subprocess import run
    run(f"quarto preview query.qmd --port 8080 {'--no-browser' if not browser else ''}", )


if __name__ == '__main__':
    query()