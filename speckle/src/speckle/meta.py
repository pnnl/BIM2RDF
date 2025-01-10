
class object:
    @staticmethod
    def uri(project_id, object_id=''):
        from .config import server
        return f"https://{server}/projects/{project_id}/objects/{object_id}"


class prefixes:
    from bim2rdf.rdf import NameSpace
    concept =   NameSpace('spkl',       "urn:speckle:concept")
    meta =      NameSpace('spkl.meta',  "urn:speckle:meta")

