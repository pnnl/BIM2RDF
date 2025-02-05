
def test_engine():
    from bim2rdf.engine import Run
    _ = Run().run(ttls=['223p.ttl'], project_name='test', model_name='main')
    print(len(_))


if __name__ ==  '__main__':
    test = test_engine
    test()
