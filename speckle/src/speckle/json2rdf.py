


def to_rdf(d, *p, project_id, **k):
    from speckle import object_uri, base_uri
    from json2rdf.json2rdf import to_rdf as to_rdf
    return to_rdf(
        d, *p,
        subject_id_keys=('id',),
        object_id_keys=('referencedId', 'connectedConnectorIds'),
        array_keys={'matrix', 'data'},
        key_prefix=('spkl', base_uri()),
        id_prefix=('spkl.data', object_uri(project_id=project_id)),
        meta_prefix=('meta',"http://meta",),
        **k)



if __name__ == '__main__':
    from pathlib import Path
    from .data import get_json

    def json(project_id, object_id,
             o=Path('data.json'), ):
        """gets json"""
        _ = get_json(project_id, object_id)
        o = Path(o)
        from json import dump
        dump(_, open(o, 'w'), indent=1)
        return o
    
    def ttl(project_id=None, object_id=None,
            i=None,
            o=Path('data.ttl'),):
        """gets json and converts it to ttl"""
        o = Path(o)
        if not i:
            _ = get_json(project_id, object_id)
        else:
            i = Path(i)
            assert(i.exists())
            _ = open(i).read()
        _ = to_rdf(_, project_id='project_id' if not project_id else project_id)
        open(o, 'w').write(_)
        return o

    import fire
    fire.Fire({
        'json': json,
        'ttl': ttl,})


