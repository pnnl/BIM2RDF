
class Object: # entity?
    __slots__ = 'id', 'data'
    def __init__(self, id, data) -> None:
        self.id = id
        self.data = data # self-refs :/
    
    def __repr__(self) -> str:
        return f"@{self.id} {repr(self.data)}"

    def update(self, items):
        if isinstance(self.data, list):
            self.data.extend(v for k,v in items)
        else:
            assert(isinstance(self.data, dict))
            self.data.update(items)
    
    def __iter__(self):
        if isinstance(self.data, type(self)):
            yield from self.data
        elif isinstance(self.data, list):
            yield from enumerate(self.data)
        else:
            assert(isinstance(self.data, dict))
            yield from self.data.items()


class MatrixList(list):
    def __str__(self, ):
        return "encoded matrix list"

terminals = {
    int, float,
    str,
    bool,
    type(None), # weird
    # does json have datetime?
    MatrixList, # don't traverse these if matrix
    }
terminals = tuple(terminals)



class Remapping:

    def __init__(self, d) -> None:
        self.data = d

    @classmethod
    def map(cls, d):
        from boltons.iterutils import remap 
        return remap(d,
                visit=cls.visit,
                enter=cls.enter,
                exit=cls.exit,
                )
    
    def __call__(self):
        return self.map(self.data)


class Identification(Remapping):
    """
    json -> objects with id
    """
    @classmethod
    def visit(cls, p, k, v): # path, key, value
        # keep for transformations?
        return True
    
    @classmethod
    def enter(cls, p, k, v):
        # for creating 'parents'
        # and id'ing things
        ids = {'referencedId', 'id'}
        def dicthasid(v): # dont mod dict
            for id in ids:
                if id in v:
                    return id
        if isinstance(v, dict):
            did = dicthasid(v)
            items = v.items() if did is None else ((k,v) for k,v in v.items() if k !=did )
            return Object(v[did] if did is not None else id(v), {}), items
        elif isinstance(v, list):
            #from uuid import uuid4 as uid
            # python already creates an id. just use it
            return Object(id(v), []), enumerate(v)  # why do i have to enum?
        else:
            assert(isinstance(v, terminals))
            return v, False

    @classmethod
    def exit(cls, p, k, v,
            new_obj, new_items):
        if isinstance(new_obj, Object):
            new_obj.update(new_items)
        else:
            raise Exception('not handled')
            #assert(isinstance(new_obj, list))
            #new_obj.extend(v for i,v in new_items)
        return new_obj
    

class Tripling(Remapping):
    """
    (identified) objects -> triples
    """
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Triple:
        subject: 's'
        prediate: 'p'
        object: 'o'

        def __str__(self) -> str:
            return f"{self.subject} {self.prediate} {self.object}."

    @classmethod
    def visit(cls, p, k, v):
        return True
    
    @classmethod
    def enter(cls, p, k, v):
        from itertools import chain
        if isinstance(v, Object):
            return [], ((ik, cls.Triple(v.id, ik, iv)) for ik,iv in iter(v) )
        else:
            assert(isinstance(v, cls.Triple))
            if isinstance(v.object, Object): # some "nesting"
                ptr_to_nested = []# [ ('sdfsdff', cls.Triple(v.subject, v.prediate, v.object.id)  )  ]
                nested = ((ik, cls.Triple(v.object.id, ik, iv)) for ik,iv in iter(v.object) )
                return [], (chain(ptr_to_nested, nested))
            else:
                return v, False

    @classmethod
    def exit(cls, p, k, v,
            new_obj, new_items):
        if isinstance(new_obj, list):
            new_obj.extend(v for k,v in new_items)
        else:
            raise Exception('not handled')
        return new_obj
    
    @classmethod
    def map(cls, d, progress=False):
        _ = super().map(d) # just creating triples (in nesting) is fast!
        return _
        def xflatten_iter(iterable, did=set()):
            # most intensive part for some reason
            # from boltons.iterutils import flatten_iter as flatten
            # more optimized of
            """``flatten_iter()`` yields all the elements from *iterable* while
            collapsing any nested iterables.

            >>> nested = [[1, 2], [[3], [4, 5]]]
            >>> list(flatten_iter(nested))
            [1, 2, 3, 4, 5]
            """
            for i in iterable:
                if isinstance(i, list):
                    yield from flatten_iter(i, did=did)
                else:
                    assert(isinstance(i, cls.Triple))
                    if i not in did:
                        did.add(i)
                        yield 1
                    else:
                        sdf
                        continue
            # for item in iterable:
            #     if isinstance(item, list):
            #         yield from flatten_iter(item)
            #     else:
            #         yield item
        from boltons.iterutils import flatten_iter
        _ = flatten_iter(_)
        #from tqdm import tqdm
        #_ = tqdm(_)
        _ = list(_)
        return _



# RDFing
# obj that are sub



def json():
    return { "stream": {"id": 'sid', "object": {'id': 'oid',
    'p1': 123,
    'p2': 'abc',}},}

def json():
    # connector triple is   (1, lp, 2)
    return {'id':1, 'p': 3, 'lp': {'id': 2, 'p': 'np'}  }

def json():
    return {'id':3, 'l': [1,2, {'id': 5, 'pl': 'p'}  ] }


from functools import cache
@cache
def bigjson():
    from json import load
    _ = load(open('./data.json'))
    #_ = _['stream']['object']['data'] # ok
    #_ = _['stream']['object']['children']['objects'][0]['data']['parameters']
    return _

@cache
def badjson():
    #from json import load
    #return load(open('./bad.json'))
    _ = """
{
    "id": "5fd0c7fb45bc28ceb05176792e8b866d",
    "Width": {
        "id": "cfae8a1f16097bae925471679ec32abd",
        "name": "Width",
        "units": null,
        "value": 2,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Width"
    },
    "Length": {
        "id": "19510fa4dcda3176ac9a84b8b21d22ab",
        "name": "Length",
        "units": null,
        "value": 2,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Length"
    },
    "DOOR_COST": {
        "id": "b2741f73de2fe0ae177535ad42e84d83",
        "name": "Cost",
        "units": "฿",
        "value": null,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:currency-1.0.0",
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "DOOR_COST"
    },
    "speckle_type": "Base",
    "ALL_MODEL_URL": {
        "id": "5464afb207cd81975a9a85b6e693ba9a",
        "name": "URL",
        "units": null,
        "value": "http://www.finelite.com/index.php",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_URL"
    },
    "Center Shield": {
        "id": "69cd8893f6b168f56d64a88ad55ab4b7",
        "name": "Center Shield",
        "units": null,
        "value": 0.4166666666666667,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Center Shield"
    },
    "KEYNOTE_PARAM": {
        "id": "d14e110c3edf5ddbe4eacd13c46d7fd1",
        "name": "Keynote",
        "units": null,
        "value": null,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "KEYNOTE_PARAM"
    },
    "applicationId": null,
    "OMNICLASS_CODE": {
        "id": "b75af5017b17f1a11641d8f261601929",
        "name": "OmniClass Number",
        "units": null,
        "value": "",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "OMNICLASS_CODE"
    },
    "UNIFORMAT_CODE": {
        "id": "8ed423285d1d5d7118b7a43e40b32883",
        "name": "Assembly Code",
        "units": null,
        "value": "",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "UNIFORMAT_CODE"
    },
    "WINDOW_TYPE_ID": {
        "id": "26cb8c6672222ea4b2b347d1f78977d8",
        "name": "Type Mark",
        "units": null,
        "value": "Luminaire9",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "WINDOW_TYPE_ID"
    },
    "ALL_MODEL_MODEL": {
        "id": "e1ab11882cd71a59bfc05a20f44e87ba",
        "name": "Model",
        "units": null,
        "value": "HPR LED-EP-A-2x4-DCO-SO-3500K-120-C1--OBD",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_MODEL"
    },
    "DESIGN_OPTION_ID": {
        "id": "226f48801e3084d3491eb079e8dd0af8",
        "name": "Design Option",
        "units": null,
        "value": "-1",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "DESIGN_OPTION_ID"
    },
    "FBX_LIGHT_WATTAGE": {
        "id": "73abeca540415fb5cc14ce1b47d9591f",
        "name": "Wattage",
        "units": "W",
        "value": 39.29,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:watts-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_WATTAGE"
    },
    "SYMBOL_NAME_PARAM": {
        "id": "3949c73b722527275423bb9dfd37b3cb",
        "name": "Type Name",
        "units": null,
        "value": "Luminaire9",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "SYMBOL_NAME_PARAM"
    },
    "FBX_LIGHT_EFFICACY": {
        "id": "f8e220fdb404192c8cc708ffe52b8537",
        "name": "Efficacy",
        "units": "lm/W",
        "value": 148.54196375059416,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:lumensPerWatt-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_EFFICACY"
    },
    "totalChildrenCount": 0,
    "ELEM_CATEGORY_PARAM": {
        "id": "f5c32b3f20e121f82ef1ffcb984bdd3a",
        "name": "Category",
        "units": null,
        "value": "-2001120",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ELEM_CATEGORY_PARAM"
    },
    "ALL_MODEL_TYPE_IMAGE": {
        "id": "e6417f0a96a3c38d9a622ab5494e8612",
        "name": "Type Image",
        "units": null,
        "value": "-1",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_TYPE_IMAGE"
    },
    "ALL_MODEL_DESCRIPTION": {
        "id": "207a93dd3ef94e5d96e23b3ae8295820",
        "name": "Description",
        "units": null,
        "value": "Recessed High Performance LED",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_DESCRIPTION"
    },
    "ALL_MODEL_FAMILY_NAME": {
        "id": "d8011153150f5b91a7bc7165fdab39cd",
        "name": "Family Name",
        "units": null,
        "value": "Lighting-Recessed-Finelite-HPR-LED-EP",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_FAMILY_NAME"
    },
    "FBX_LIGHT_ILLUMINANCE": {
        "id": "5516876c20335fb2c3b74c9066fad0b1",
        "name": "Illuminance",
        "units": "lx",
        "value": 49.99095122023209,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:lux-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_ILLUMINANCE"
    },
    "LIGHTING_FIXTURE_LAMP": {
        "id": "82d45de2b5582776f89f55fda87a9952",
        "name": "Lamp",
        "units": null,
        "value": "LED",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "LIGHTING_FIXTURE_LAMP"
    },
    "OMNICLASS_DESCRIPTION": {
        "id": "1ff48b1d6e07459451e87d61fb809f18",
        "name": "OmniClass Title",
        "units": null,
        "value": "",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "OMNICLASS_DESCRIPTION"
    },
    "UNIFORMAT_DESCRIPTION": {
        "id": "026207f8c83f70e3dccb1c9d4f0a195c",
        "name": "Assembly Description",
        "units": null,
        "value": "",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "UNIFORMAT_DESCRIPTION"
    },
    "ALL_MODEL_MANUFACTURER": {
        "id": "90900972e9cc72dbecff5c8eac6f9335",
        "name": "Manufacturer",
        "units": null,
        "value": "Finelite, Inc.",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_MANUFACTURER"
    },
    "ELEM_CATEGORY_PARAM_MT": {
        "id": "efd433a00f829353bdebddfe63a56b2f",
        "name": "Category",
        "units": null,
        "value": "-2001120",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ELEM_CATEGORY_PARAM_MT"
    },
    "FBX_LIGHT_COLOR_FILTER": {
        "id": "71614c9bd3e4a75b92ae740ff0a03a22",
        "name": "Color Filter",
        "units": null,
        "value": 16777215,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_COLOR_FILTER"
    },
    "Luminaire Style - Flat": {
        "id": "664978d86af15192416af3e63440bda5",
        "name": "Luminaire Style - Flat",
        "units": null,
        "value": true,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Luminaire Style - Flat"
    },
    "RBS_ELEC_APPARENT_LOAD": {
        "id": "687cf17fc01f6a6c5b4d4a611e0694a0",
        "name": "Apparent Load",
        "units": "VA",
        "value": 0,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:voltAmperes-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "RBS_ELEC_APPARENT_LOAD"
    },
    "ALL_MODEL_TYPE_COMMENTS": {
        "id": "389eba7a64948e921f41b0f13cab0ff8",
        "name": "Type Comments",
        "units": null,
        "value": null,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": true,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ALL_MODEL_TYPE_COMMENTS"
    },
    "FBX_LIGHT_LIMUNOUS_FLUX": {
        "id": "9adf0d86423f1b43b4b49da036d50c43",
        "name": "Luminous Flux",
        "units": "lm",
        "value": 5836.213755760845,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:lumens-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_LIMUNOUS_FLUX"
    },
    "LIGHTING_FIXTURE_WATTAGE": {
        "id": "6e8019b73f81c0b27016df0c5695367f",
        "name": "Wattage Comments",
        "units": null,
        "value": null,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "LIGHTING_FIXTURE_WATTAGE"
    },
    "Luminaire Style - Angled": {
        "id": "9c43f090406c4b8774906e274cb6d212",
        "name": "Luminaire Style - Angled",
        "units": null,
        "value": true,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Luminaire Style - Angled"
    },
    "FBX_LIGHT_SPOT_TILT_ANGLE": {
        "id": "6a6365cee2723df0cd3a95b389f0cdd3",
        "name": "Tilt Angle",
        "units": "°",
        "value": -90,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:degrees-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_SPOT_TILT_ANGLE"
    },
    "FBX_LIGHT_LOSS_FACTOR_CTRL": {
        "id": "4f314517f466ced28f84ae7203c0435e",
        "name": "Light Loss Factor",
        "units": null,
        "value": 0,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_LOSS_FACTOR_CTRL"
    },
    "FBX_LIGHT_PHOTOMETRICS_FAM": {
        "id": "b0008d6d6c2f2e1e057f613b4573049e",
        "name": "Light Source Definition (family)",
        "units": null,
        "value": "Rectangle+Photometric Web",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_PHOTOMETRICS_FAM"
    },
    "FBX_LIGHT_PHOTOMETRIC_FILE": {
        "id": "b5c09c44498efb3dde30986cd67f5a4c",
        "name": "Photometric Web File",
        "units": null,
        "value": "T25411.IES",
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_PHOTOMETRIC_FILE"
    },
    "FBX_LIGHT_TOTAL_LIGHT_LOSS": {
        "id": "27d8f1476470f7e42585136e25e5d28d",
        "name": "Total Light Loss Factor",
        "units": null,
        "value": 1,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:general-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_TOTAL_LIGHT_LOSS"
    },
    "FBX_LIGHT_INITIAL_INTENSITY": {
        "id": "8b7b8a365961b4e51ae85758c71608cb",
        "name": "Initial Intensity",
        "units": null,
        "value": 0,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_INITIAL_INTENSITY"
    },
    "STRUCTURAL_FAMILY_CODE_NAME": {
        "id": "d9e23cc21311d6878acf9df17a045f8c",
        "name": "Code Name",
        "units": null,
        "value": "",
        "isShared": false,
        "isReadOnly": true,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "STRUCTURAL_FAMILY_CODE_NAME"
    },
    "FAMILY_WPB_DEFAULT_ELEVATION": {
        "id": "b80ef315e0c4f122fc7a1c3f4a612e12",
        "name": "Default Elevation",
        "units": null,
        "value": 4,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FAMILY_WPB_DEFAULT_ELEVATION"
    },
    "FBX_LIGHT_EMIT_SHAPE_VISIBLE": {
        "id": "ef80abb74d0e2dcdbc19509dbca73982",
        "name": "Emit Shape Visible in Rendering",
        "units": null,
        "value": false,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_EMIT_SHAPE_VISIBLE"
    },
    "FBX_LIGHT_INITIAL_COLOR_CTRL": {
        "id": "655080992e677ff7f9c949e307330e84",
        "name": "Initial Color",
        "units": null,
        "value": 0,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_INITIAL_COLOR_CTRL"
    },
    "FBX_LIGHT_LIMUNOUS_INTENSITY": {
        "id": "d6a171a74451d194214b7870a14a9fa0",
        "name": "Luminous Intensity",
        "units": "cd",
        "value": 464.43113408512704,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:candelas-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_LIMUNOUS_INTENSITY"
    },
    "FBX_LIGHT_DIMMING_LIGHT_COLOR": {
        "id": "b77ca4a602e5aa6e9b439da8958cdf1e",
        "name": "Dimming Lamp Color Temperature Shift",
        "units": null,
        "value": 0,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_DIMMING_LIGHT_COLOR"
    },
    "FBX_LIGHT_EMIT_RECTANGLE_WIDTH": {
        "id": "c44335fad081a4f232e5100f22bd9e85",
        "name": "Emit from Rectangle Width",
        "units": null,
        "value": 2,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_EMIT_RECTANGLE_WIDTH"
    },
    "FBX_LIGHT_EMIT_RECTANGLE_LENGTH": {
        "id": "9fb142593b62261f134331fc546be647",
        "name": "Emit from Rectangle Length",
        "units": null,
        "value": 2,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:feetFractionalInches-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_EMIT_RECTANGLE_LENGTH"
    },
    "FBX_LIGHT_INITIAL_COLOR_TEMPERATURE": {
        "id": "42a21d25bf0e02cc3286d69009bae126",
        "name": "Initial Color Temperature",
        "units": "K",
        "value": 3200,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:kelvin-1.0.0",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "FBX_LIGHT_INITIAL_COLOR_TEMPERATURE"
    },
    "0b538507-88db-4d93-9a9c-6903adcc42a6": {
        "id": "ee5db0dfab41ab32ae4a17b587941d66",
        "name": "Power Factor",
        "units": null,
        "value": 1,
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:general-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "0b538507-88db-4d93-9a9c-6903adcc42a6"
    },
    "0e4c8c80-2e2b-4d72-ac7d-1d0f9242de43": {
        "id": "f7096f27bd9f6c7068c6d77a2b83607a",
        "name": "Integrated Sensors",
        "units": null,
        "value": "Daylight",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "0e4c8c80-2e2b-4d72-ac7d-1d0f9242de43"
    },
    "6b663138-b86b-4494-ae66-626d4032fc6c": {
        "id": "b5cc48bd239cc3179b209d08871ec37c",
        "name": "Ceiling Type",
        "units": null,
        "value": "1” T-Bar",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "6b663138-b86b-4494-ae66-626d4032fc6c"
    },
    "7e22f27c-2be9-49f5-8d98-666ecb836c02": {
        "id": "8802245e09fcdb2655e9f4db6fc34a90",
        "name": "Size",
        "units": null,
        "value": "2x2",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "7e22f27c-2be9-49f5-8d98-666ecb836c02"
    },
    "82dbc3e6-0600-4650-9ba7-bfbe3a9b3fd1": {
        "id": "e49469c6b39d701906cc7c126cad326b",
        "name": "Luminaire Styles",
        "units": null,
        "value": "Angled",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "82dbc3e6-0600-4650-9ba7-bfbe3a9b3fd1"
    },
    "9fb38f69-4b06-438b-897c-310ef9fe0396": {
        "id": "8b97635656b00a3cf1d48450e058a5c7",
        "name": "Optic",
        "units": null,
        "value": "Diffuse",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "9fb38f69-4b06-438b-897c-310ef9fe0396"
    },
    "Luminaire Style - Angled Narrow Rail": {
        "id": "484a836e79e8e833a31faf0f505af650",
        "name": "Luminaire Style - Angled Narrow Rail",
        "units": null,
        "value": true,
        "isShared": false,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "Luminaire Style - Angled Narrow Rail"
    },
    "b5957107-d435-417c-bbb5-cab227666e6b": {
        "id": "f4493fc8923d444a367187a064fedb59",
        "name": "IES File Link",
        "units": null,
        "value": "http://www.finelite.com/download_files/series_downloads/IES/HPR-LED/2X4/IES_HPR-LED_2X4.zip",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "b5957107-d435-417c-bbb5-cab227666e6b"
    },
    "cde9e80b-6eab-48c4-9463-e65c64336483": {
        "id": "f5fe42e2b1dc0cce8e6cec6d699a3ac1",
        "name": "LED Color Temperature",
        "units": null,
        "value": "3500K",
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "cde9e80b-6eab-48c4-9463-e65c64336483"
    },
    "cec2e9cb-9151-4b72-a3a6-2ebda7e2b2d4": {
        "id": "f71ffde7ba9e13f09a618360ff82a36e",
        "name": "Number of Poles",
        "units": null,
        "value": 1,
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": null,
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "cec2e9cb-9151-4b72-a3a6-2ebda7e2b2d4"
    },
    "ee1f8bb8-e503-49a8-bd5b-170d64400d82": {
        "id": "b231ea2d0d8d805978a5e394fc2c1b18",
        "name": "Voltage",
        "units": "V",
        "value": 119.99999999999999,
        "isShared": true,
        "isReadOnly": false,
        "speckle_type": "Objects.BuiltElements.Revit.Parameter",
        "applicationId": null,
        "applicationUnit": "autodesk.unit.unit:volts-1.0.1",
        "isTypeParameter": false,
        "totalChildrenCount": 0,
        "applicationUnitType": null,
        "applicationInternalName": "ee1f8bb8-e503-49a8-bd5b-170d64400d82"
    }
}
"""
    from json import loads
    #_ = '{"id":3, "p": {"id": "sdfsdf" } }'
    _ = loads(_)
    return _

def test():
    _ = badjson()
    #_ = [{'id':i, 'p':f"{i}"} for i in range(1)]
    _ = Identification.map(_)
    _ = Tripling.map(_)
    return _

