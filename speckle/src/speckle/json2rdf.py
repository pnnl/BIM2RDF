from json2rdf.json2rdf import *

if __name__ == '__main__':
    from pathlib import Path
    from .data import get_json

    def json(project_id, object_id,
             path=Path('data.json'), ):
        """gets json"""
        _ = get_json(project_id, object_id)
        path = Path(path)
        from json import dump
        dump(_, open(path, 'w'), indent=1)
        return path
    
    def ttl(project_id, object_id,
            path=Path('data.ttl'),):
        """gets json and converts it to ttl"""
        path = Path(path)
        _ = get_json(project_id, object_id)
        _ = to_rdf(_)
        open(path, 'w').write(_)
        return path

    import fire
    fire.Fire({
        'json': json,
        'ttl': ttl,})


