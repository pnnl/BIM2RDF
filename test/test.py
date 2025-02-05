
def test_engine():
    from bim2rdf.engine import Run
    Run().run(ttls=['223p.ttl'], project_name='test', model_name='main')


if __name__ ==  '__main__':
    test = test_engine
    test()
