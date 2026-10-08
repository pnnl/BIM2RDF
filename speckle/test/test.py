

def test():
    import bim2rdf.speckle.data as sd
    p = sd.Project.from_name("Pritoni")
    _ = p.models[0].versions[0].parquets
    return _
    m = p.models[0]
    v = m.versions[0]
    p = p.id #"9e62692a26"
    m = m.id #"f515d35487"
    v = v.id#"dd38e48235"
    import bim2rdf.speckle.rest as sr
    _ = sr.artifacts(project_id=p, model_id=m, version_id=v)
    return _

if __name__ == '__main__':
    print(
    test()
    )
