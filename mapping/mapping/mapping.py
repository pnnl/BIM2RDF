from rdflib import Graph
from . import mapping_dir
from typing import Iterator, Generator, Tuple, Literal, Union
from typing import overload
from pathlib import Path
from phantom.base import Phantom
from . import schema as s


def is_sqldb(file: Path):
    import sqlite3
    con = sqlite3.connect(file)
    try:
        con.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        return True
    except:
        return False
class SQLiteDB(Path, Phantom, predicate=is_sqldb): ...


def properties_lines(d: dict) -> Iterator[str]:
    for k,v in d.items():
        yield f"{k}={str(v).lower() if isinstance(v, bool) else v}"

def is_path(s: str) -> bool: return Path(s).exists()
class PathStr(str, Phantom, predicate=is_path): ...

class ShortName(str, Phantom, predicate=lambda n: not s.DBPropertyName.__predicate__(n) ): ...

from attrs import frozen as dataclass


@dataclass
class DBProperty(s.DBProperty, ):
    name:   s.DBPropertyName
    value:  str

    @classmethod
    def make(cls, short_name: ShortName, value: str) -> 'DBProperty':
        return cls(s.DBPropertyName(f"jdbc.{short_name}"), value)

    def __str__(self) -> s.PropertyStr:
        return s.PropertyStr(f"{self.name}={self.value}")


@dataclass
class DBProperties(s.DBProperties):
    """implementation is specific to sqlite case"""
    name:   DBProperty
    url:    DBProperty
    driver: DBProperty
    user:   DBProperty
    
    @classmethod
    def make(cls, file: SQLiteDB) -> 'DBProperties':
        return cls.sqlite(file)

    @classmethod
    def sqlite(cls, file: SQLiteDB) -> 'DBProperties':
        # need to create a stripped version to a file
        # bc the mapping program needs starts separately
        stripped = file.parent / (file.stem  + '_stripped' + file.suffix )
        if stripped.exists(): stripped.unlink()
        import sqlite3
        con = sqlite3.connect(stripped)
        cur = con.cursor()
        # for some reason, ontop didnt like sqlite constraints
        for line in cls.constraint_stripper(file):
            cur.execute(line)
        con.commit()
        return cls(
            name =      DBProperty.make(ShortName('name'),      'sqldb'),
            url =       DBProperty.make(ShortName('url'),       f"jdbc:sqlite:{stripped.name}"),
            driver =    DBProperty.make(ShortName('driver'),    'org.sqlite.JDBC'),
            user =      DBProperty.make(ShortName('user'),      'user'))

    @classmethod
    def constraint_stripper(cls, sqlitedb: SQLiteDB) -> Iterator[str]:
        # hack: for some reason ontop doesnt work if sqlite has constraints
        import sqlite3
        src = sqlite3.connect(str(sqlitedb))
        table_query = """\
        SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';
        """
        tables = src.execute(table_query)
        #def table_schema(tbl: str) -> str:
        #    return f"SELECT sql FROM sqlite_master WHERE name='{tbl}';"
        for line in src.iterdump():
            if 'create table' in line.lower():
                line = cls.strip_constraint(line)
            yield line
    
    @staticmethod
    def strip_constraint(tbl_schema: str) -> str:
        # todo: inelegant
        has_constraint = lambda s: ('constraint "' in s.lower()) or ('primary key' in s.lower())
        if not has_constraint(tbl_schema):
            return tbl_schema
        else:
            parts = []
            for part in tbl_schema.split(','):
                if not has_constraint(part): parts.append(part)
                else: break # expecting contraints to be last
            tbl_schema = ','.join(parts)
            tbl_schema += ')'
            assert(not has_constraint(tbl_schema))
            return tbl_schema

    def lines(self):
        from attrs import asdict
        _ = asdict(self)
        _ = {k:v['value'] for k,v in _.items()}
        return properties_lines(_)

    def __str__(self) -> str:
        return '\n'.join(self.lines())


@dataclass
class OntopProperties(s.OntopProperties):
    inferDefaultDatatype: bool

    @classmethod
    def make(cls,) -> 'OntopProperties':
        return cls(True)

    def lines(self) -> Iterator[str]:
        from attrs import asdict
        _ = asdict(self)
        return properties_lines(_)
    
    def __str__(self) -> str:
        return '\n'.join(self.lines())


@dataclass
class Properties(s.Properties):
    jdbc:   DBProperties
    ontop:  OntopProperties

    @classmethod
    def make(cls, sqlite: SQLiteDB)     -> 'Properties':
        return cls.from_sqlite(sqlite)

    @classmethod
    def from_sqlite(cls, sqlite: SQLiteDB)  -> 'Properties':
        d = DBProperties.make(sqlite)
        o = OntopProperties.make()
        return cls(d, o)


    def lines(self) -> Iterator[str]:
        from attrs import asdict
        for k,v in asdict(self, recurse=False).items():
            for line in v.lines():
                yield f"{k}.{line}" # just prefix

    def __str__(self):
        return '\n'.join(self.lines())


@dataclass
class Map(s.Map):
    id:     s.KeyStr
    source: s.SQL
    target: s.templatedTTL

    @classmethod
    def make(cls, *p, **k) -> 'Map':
        return cls(id=k['id'], source=k['source'], target=k['target'])
    

def is_yaml(path: Path) -> bool:
    import yaml
    try:
        yaml.safe_load(open(path))
        return True
    except:
        return False    
class YamlFile(Path, Phantom, predicate=is_yaml): ...


@dataclass
class Building(s.Building):
    name:       str

    @overload
    @classmethod
    def make(cls, i: str)               -> 'Building': ...
    @overload
    @classmethod
    def make(cls, i: 'Building')        -> 'Building': ...
    @classmethod
    def make(cls, i: 'str | Building')  -> 'Building':
        return i if isinstance(i, Building) else Building(i)

    def uri(self, domain: str  = 'example.com') -> s.URI:
        return s.URI(f"http://{domain}/{self.name}")
    
@dataclass
class Prefix(s.Prefix):
    name:   s.KeyStr
    uri:    s.URI

prefix = Prefix(s.KeyStr('pnnl'), s.URI('http://example.com/'))


@dataclass
class MappingCallouts(s.MappingCallouts):
    prefix:     Prefix
    building:   Building

    @classmethod
    def make(cls, p: Prefix, b: Building) -> 'MappingCallouts':
        if p.uri.endswith(b.name):  return cls(p, b)
        else:
            return cls(
                        Prefix(
                            s.KeyStr(p.name),
                            s.URI(p.uri + b.name) if p.uri.endswith('/') \
                            else s.URI(f"{p.uri}/{b.name}")),
                        b)


@dataclass
class SQLRDFMap(s.SQLRDFMap):
    prefixes:   s.Prefixes | None
    maps:       s.Maps

    @overload
    @classmethod
    def _make(cls, i: dict)     -> 'SQLRDFMap': ...
    @overload
    @classmethod
    def _make(cls, i: YamlFile) -> 'SQLRDFMap': ...
    @overload
    @classmethod
    def _make(cls, i: str)      -> 'SQLRDFMap': ...

    @classmethod
    def _make(cls, i: dict | YamlFile | str) -> 'SQLRDFMap':
        if      isinstance(i, dict):        return cls.from_dict(       i)
        elif    isinstance(i, YamlFile):    return cls.from_yamlfile(   i)
        elif    isinstance(i, str):         return cls.from_name(       i)
        else:   raise TypeError

    @classmethod
    def make(cls,
        i: dict | YamlFile | str,
        callouts: MappingCallouts | None = MappingCallouts.make(prefix, Building('unnamed') )) -> 'SQLRDFMap':
        self: SQLRDFMap = cls._make(i)
        if not callouts: return self
        if not (self.callouts == callouts):
            #from attrs import evolve
            pfxs =  dict(self.prefixes) if self.prefixes else dict()
            pfxs.update({callouts.prefix.name: callouts.prefix.uri})
            return cls(pfxs, self.maps)
        else:
            return self

    @property
    def callouts(self) -> MappingCallouts | None:
        if self.prefixes:
            if pfx_name := prefix.name if prefix.name in self.prefixes else None:
                return \
                    MappingCallouts(
                        Prefix(
                            pfx_name,
                            s.URI(self.prefixes[pfx_name]) ),
                        Building.make(self.prefixes[pfx_name].split('/')[-1]))
        return None
    
    @classmethod
    def from_dict(cls, d: dict) -> 'SQLRDFMap':
        prefixes = d['prefixes'] if 'prefixes' in d else None
        prefixes = {s.KeyStr(k):s.URI(v) for k,v in prefixes.items()} if prefixes else None
        maps = d['maps'] if 'maps' in d else []
        maps = [Map.make(id=m['id'], source=m['source'], target=m['target']) for m in maps]
        return cls(prefixes=prefixes, maps=maps)

    @classmethod
    def from_yamlfile(cls, path: YamlFile) -> 'SQLRDFMap':
        import yaml
        return cls.from_dict(yaml.safe_load(open(path)))

    @classmethod
    def from_name(cls, name: str) -> 'SQLRDFMap':
        return cls.from_yamlfile( YamlFile(mapping_dir / name / 'maps.yaml') )

        
    def make_obda(self) -> str:
        from jinja2 import Environment, FileSystemLoader#, select_autoescape
        env = Environment(loader=FileSystemLoader(mapping_dir))

        def strip_comments(lines):
            lines = lines.split('\n')
            o = ""
            for ln in lines:
                o += ln.split('#', 1)[0]
                o += ' ' # need a lil space sometimes
            assert('#' not in o)
            return o
        from attr import asdict
        d = asdict(self)
        for map in d['maps']:
            map['target'] = strip_comments(map['target'])
            map['source'] = strip_comments(map['source'])
        _ =  env.get_template('obda.jinja').render(**d)
        return _

    def __str__(self) -> str:
        return self.make_obda()
    


def get_workspace(loc: Path= mapping_dir / 'work') -> Path:
    if not loc.exists():
        loc.mkdir()
    else:
        from shutil import rmtree
        rmtree(loc)
        loc.mkdir()
    return loc


@dataclass
class OntologyBase(s.OntologyBase):
    name:   str

    @property
    def graph(self):
        from ontologies import get
        return get(self.name)


    @classmethod
    def s(cls, *p, **k) -> Generator['OntologyBase', None, None]:
        from ontologies import names
        for n in names: yield cls(n)


@dataclass
class OntologyCustomization(s.OntologyCustomization):
    base:               OntologyBase

    @overload
    @classmethod
    def make(cls, name: str, /)                -> 'OntologyCustomization': ...
    @overload
    @classmethod
    def make(cls, base: OntologyBase, /)       -> 'OntologyCustomization': ...
    @classmethod
    def make(cls, i: str | OntologyBase )   -> 'OntologyCustomization':
        if      isinstance(i, str): return cls( OntologyBase(i) )
        else:                       return cls(i)
    
    @property
    def graph(self) -> Graph:
        def turtle_soup(loc: Path):
            g = s.Graph()
            for f in (f for f in ( loc ).iterdir() if f.suffix == '.ttl'):
                g += s.Graph().parse(f)
            return g
        cstm = turtle_soup(mapping_dir / self.base.name)
        return cstm


@dataclass
class Ontology(s.Ontology):
    base:           OntologyBase
    customization:  OntologyCustomization
    
    @classmethod
    def make(cls, name: str, /)             -> 'Ontology':
        oc = OntologyCustomization.make(name)
        return cls(oc.base, oc)
    
    @property
    def graph(self) -> s.Graph:
        return self.base.graph + self.customization.graph


@dataclass
class SQLRDFMapping(s.SQLRDFMapping):
    ontology:   Ontology
    mapping:    SQLRDFMap
    properties: Properties


    @classmethod
    def make(cls, 
            bdg:                    Building | str,
            customization_name:     str,
            db:                     SQLiteDB,
            ) ->                    'SQLRDFMapping':
        return cls(
            *cls.from_customizations(bdg, customization_name),
            cls.from_sqlite(db))

    @classmethod
    def from_customizations(cls, bdg: Building | str, name: str) -> Tuple[Ontology, SQLRDFMap]:
        o = Ontology.make(name)
        m = SQLRDFMap.from_name(o.base.name)
        return o, m

    @classmethod
    def from_sqlite(cls, db: SQLiteDB) -> Properties:
        return Properties.from_sqlite(db)


    @overload 
    def writer(self, part: Ontology,)       -> 'OntologyWriting':   ...
    @overload
    def writer(self, part: SQLRDFMap,)      -> 'MappingWriting':    ...
    @overload
    def writer(self, part: Properties, )    -> 'PropertiesWriting': ...
    def writer(self, part: Ontology | SQLRDFMap | Properties,) \
            -> Union['OntologyWriting', 'MappingWriting', 'PropertiesWriting']:
        if      isinstance(part, Ontology):     return OntologyWriting.make(    part)
        elif    isinstance(part, SQLRDFMap):    return MappingWriting.make(     part)
        elif    isinstance(part, Properties):   return PropertiesWriting.make(  part)
        else:   raise NotImplementedError
    

    def map(self, dir: s.Dir)           -> s.ttlFile:
        """the 'do' """
        ow = self.writer(self.ontology   )#.write(    dir)
        mw = self.writer(self.mapping    )#.write(    dir)
        pw = self.writer(self.properties )#.write(    dir)
        out = s.ttlFile(dir / 'mapped.ttl')
        
        from shutil import which
        _ = which('ontop')
        if _:
            ontop = Path(_).absolute()
            del _
        else:
            raise RuntimeError('ontop exe not found')

        from subprocess import run
        r = run([
            ontop, 'materialize',
            '-t',                   str(ow.write(dir).name),
            '-m',                   str(mw.write(dir).name),
            '--properties',         str(pw.write(dir).name),
            '-o',                   str(out),
            '--disable-reasoning',
            '-f', 'turtle',
            '--db-password', 'sdfsdffsd' 
        ],  cwd=dir,
        shell=False, check=True,
        text=True,
        )
        assert(out.exists())
        return out


from typing import Protocol
class hasPathing(Protocol):
    @property
    def name(self)      -> str: ...
    @property
    def file_ext(self)  -> str: ...
class Writing(hasPathing):
    def path(self, dir: s.Dir) -> Path:
        return dir / f"{self.name}.{self.file_ext}"


@dataclass
class OntologyWriting(Writing, s.OntologyWriting):
    ontology: Ontology
    @property
    def file_ext(self) ->   Literal['ttl']:      return 'ttl'
    @property
    def name(self) ->       Literal['ontology']: return 'ontology'

    @classmethod
    def make(cls, *p, **k) -> 'OntologyWriting':
        return cls(p[0])

    def write(self, dir: s.Dir) -> s.Path:
        self.ontology.graph.serialize(self.path(dir), format='turtle')
        return self.path(dir)


@dataclass
class MappingWriting(Writing, s.MappingWriting):
    mapping: SQLRDFMap
    @property
    def file_ext(self) ->   Literal['obda']:    return 'obda'
    @property
    def name(self) ->       Literal['maps']:    return 'maps'

    @classmethod
    def make(cls, *p, **k) -> 'MappingWriting':
        return cls(p[0])
    
    def write(self, dir: s.Dir) -> s.Path:
        self.path(dir).write_text(str(self.mapping))
        return self.path(dir)


@dataclass
class PropertiesWriting(Writing, s.PropertiesWriting):
    properties: Properties
    @property
    def file_ext(self) ->   Literal['properties']:  return 'properties'
    @property
    def name(self) ->       Literal['sql']:         return 'sql'

    @classmethod
    def make(cls, *p, **k) -> 'PropertiesWriting':
        return cls(p[0])

    def write(self, dir: s.Dir) -> s.Path:
        self.path(dir).write_text(str(self.properties))
        return self.path(dir)

