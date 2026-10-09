

class prefixes:
    from bim2rdf.core.rdf import Prefix
    @classmethod
    def data(cls, *, name):
        return cls.Prefix(f'spkl.data.{name}', f"urn:speckle:data:{name}:")
