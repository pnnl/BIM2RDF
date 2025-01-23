
def test():
    import rules.rules as r
    r = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    _ = ''
    d = tuple(r.data(_))
    print(len(d))
    assert(d)


if __name__ ==  '__main__':
    test()