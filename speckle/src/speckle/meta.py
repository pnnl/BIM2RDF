
class object:
    @classmethod
    def uri(cls, project_id, object_id):
        from bim2rdf.config import config
        return f"https://{config.speckle.server}/projects/{project_id}/objects/{object_id}"


class prefixes:
    from bim2rdf.rdf import Prefix
    @classmethod
    def data(cls, *, project_id, object_id):
        _ = object.uri(project_id=project_id, object_id=object_id)
        return cls.Prefix('spkl.data',  _)
    concept =   Prefix('spkl',       "urn:speckle:concept:")
    meta    =   Prefix('spkl.meta',  "urn:speckle:meta:")
