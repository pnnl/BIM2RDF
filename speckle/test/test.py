


def test():
    import bim2rdf.speckle.data as sd
    p = sd.Project("d0b5d1503f")
    m = p.models[0]
    v = m.versions[0]
    j = v.json().wo_geometry()
    from json import dumps
    open('data.json', 'w').write(dumps(j, indent=2))
    t = v.ttl()
    open('data.ttl', 'w').write(t)
    #ic(j)
    #sd.json(project_id=, )


if __name__ == '__main__':
    test()