from rdflib import Graph
from . import mapping_dir
from typing import Iterator, Generator, Callable
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

# implementations
from attrs import frozen as dataclass

@dataclass
class DBProperty(s.DBProperty):
    name:   s.DBPropertyName
    value:  str

    @classmethod
    def make_unvalidated(cls, *p, **k): return cls._make(p[0], p[1])
    @classmethod
    def _make(cls, short_name: ShortName, value: str) -> 'DBProperty':
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
    # *p, **k pleases mypy
    def make_unvalidated(cls, *p, **k) -> 'DBProperties':
        return cls.sqlite(*p, **k)

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
            url =       DBProperty.make(ShortName('url'),       f"jdbc:sqlite:{stripped}"),
            driver =    DBProperty.make(ShortName('driver'),    'org.sqlite.JDBC'),
            user =      DBProperty.make(ShortName('user'),      'user'))


    @classmethod
    def constraint_stripper(cls, sqlitedb: PathStr | Path) -> Iterator[str]:
        # hack
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
        has_constraint = lambda s: ('constraint "' in s.lower()) #or ('primary key' in s.lower())
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
    def make_unvalidated(cls, *a, **k) -> 'OntopProperties':
        return cls(True)

    def lines(self):
        from attrs import asdict
        _ = asdict(self)
        return properties_lines(_)
    
    def __str__(self) -> str:
        return '\n'.join(self.lines())

@dataclass
class Properties(s.Properties):
    db:     DBProperties
    ontop:  OntopProperties

    def lines(self) -> Iterator[str]:
        from attrs import asdict
        for k,v in asdict(self, recurse=False).items():
            for line in v.lines():
                yield f"{k}.{line}" # just prefix

    def write(self, file):
        file.writelines(self.lines())

    def path(self, dir: Path,  name='sql') -> Path:
        return dir / f"{name}.properties"


@dataclass
class Map(s.Map):
    id:     s.KeyStr
    source: s.SQL
    target: s.templatedTTL

    @classmethod
    def make_unvalidated(cls, *p, **k) -> 'Map':
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
class SQLRDFMap(s.SQLRDFMap):
    prefixes:   s.Prefixes | None
    maps:       s.Maps

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

    @overload
    @classmethod
    def _make(cls, i: dict) -> 'SQLRDFMap': ...
    @overload
    @classmethod
    def _make(cls, i: YamlFile) -> 'SQLRDFMap': ...
    @overload
    @classmethod
    def _make(cls, i: str) -> 'SQLRDFMap': ...

    @classmethod
    def _make(cls, i: dict | YamlFile | str) -> 'SQLRDFMap':
        if      isinstance(i, dict):        return cls.from_dict(       i)
        elif    isinstance(i, YamlFile):    return cls.from_yamlfile(   i)
        elif    isinstance(i, str):         return cls.from_name(       i)
        else:   raise TypeError

    @classmethod
    def make_unvalidated(cls, *p, **k) -> 'SQLRDFMap': return cls._make(*p, **k)
        
    def make_obda(self) -> str:
        from jinja2 import Environment, FileSystemLoader#, select_autoescape
        env = Environment(loader=FileSystemLoader(mapping_dir))

        def strip_comments(lines):
            lines = lines.split('\n')
            o = ""
            for ln in lines:
                o += ln.split('#', 1)[0]
                o += ' ' # need a lil space sometimes
            return o
        from attr import asdict
        d = asdict(self)
        for map in self.maps:
            d['target'] = strip_comments(map.target)
            d['source'] = strip_comments(map.source)
        return env.get_template('obda.jinja').render(**d)

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
    def make_unvalidated(cls, *p, **k)  -> 'OntologyBase':
        return cls.from_name(p[0])
    
    @classmethod
    def from_name(cls, onto_name: str)  -> 'OntologyBase':
        return cls(onto_name)

    @classmethod
    def s(cls, *p, **k) -> Generator['OntologyBase', None, None]:
        from ontologies import names
        for n in names: yield cls.from_name(n)
    #def write(self, file):
        #self.graph.serialize(file, format='turtle')
    
    #def path(self, dir: Path,  name='onto'):
    #    return dir / f"{name}.ttl"


@dataclass
class Building(s.Building):
    name:   str

    @classmethod
    def make_unvalidated(cls, *p, **k) -> 'Building':
        return cls(name=p[0])

    def uri(self, prefix: str = 'example.com') -> s.URI:
        return s.URI(f"http://{prefix}/{self.name}")


@dataclass
class OntologyCustomization(s.OntologyCustomization):
    base:               OntologyBase
    building:           Building
    building_prefix:    str

    @classmethod
    def make_unvalidated(cls, *p, **k) ->                 'OntologyCustomization':
        return cls.from_customizations(*p, **k)

    @classmethod
    def from_customizations(cls, bdg: Building | str, name: str, building_prefix='example.com') ->   'OntologyCustomization':
        return cls(
            base =              OntologyBase.from_name(name),
            building =          bdg if isinstance(bdg, Building) else Building.make(str),
            building_prefix =   building_prefix)
    
    @property
    def graph(self) -> Graph:
        def turtle_soup(loc: Path):
            g = s.Graph()
            for f in (f for f in ( loc ).iterdir() if f.suffix == '.ttl'):
                g += s.Graph().parse(f)
            return g
        cstm = turtle_soup(mapping_dir / self.base.name)
        # SPECIFICS
        #@prefix bdg: <http://example.org/building/> .
        _ = cstm.namespace_manager.bind('bdg', self.building)
        return _


@dataclass
class Ontology(s.Ontology):
    base:           OntologyBase
    customization:  OntologyCustomization
    def validate(self) -> bool:
        return self.base == self.customization.base
    
    @classmethod
    def make_unvalidated(cls, *p, **k) -> 'Ontology':
        return cls.from_customizations(*p, **k)

    @classmethod
    def from_customizations(cls, *p, **k):
        c = OntologyCustomization.from_customizations(*p, **k)
        b = c.base
        return cls(b, c)
    
    @property
    def graph(self) -> s.Graph:
        return self.base.graph + self.customization.graph

    def write(self, file):
        self.graph.serialize(file, format='turtle')


class SQLRDFMapping(s.SQLRDFMapping):

    @classmethod
    def from_name(cls, name: str) -> Callable[[str, Properties], 'SQLRDFMap']:
        def o(bdg: str) -> s.Graph:
            _ = OntologyCustomization.from_name(name)(bdg).graph
            _ = _ + Ontology.from_name(name).graph
            return _
        m = Mapping.from_name(name)
        return partial(cls, mapping=m,)
        return lambda bdg, prop: cls(o(bdg), m, prop)
        
    def write(self, workspace: Path=get_workspace(),
                # just names
                ontology = 'ontology', mapping = 'maps', properties = 'sql',
                out='mapped') -> Path:
        w = workspace
        from shutil import which
        _ = which('ontop')
        if _:
            ontop = Path(_).absolute()
            del _
        else:
            raise RuntimeError('ontop exe not found')
        ontology =      w / f"{ontology}.ttl"
        mapping =       w / f"{mapping}.obda"
        properties =    w / f"{properties}.properties"
        out =           w / f'{out}.ttl'
        # clear
        for fio in {ontology, mapping, properties, out}:
            if fio.exists(): fio.unlink()
            del fio
        # write
        self.ontology.serialize(    ontology)
        self.mapping.write(open(    mapping, 'w'))
        self.properties.write(open( properties, 'w'))
        #return {'ontology', ontology, 'mapping': mapping, }
        from subprocess import run
        r = run([
            ontop, 'materialize',
            '-t',                   str(ontology),
            '-m',                   str(mapping),
            '--properties',         str(properties),
            '-o',                   str(out),
            '--disable-reasoning',
            '-f', 'turtle',
            '--db-password', 'sdfsdffsd' 
        ],  cwd=w,
        shell=False, check=True,
        )
        assert(out.exists())
        return out


    #def write(self, file: Path):
        #_ = self.make_obda()
        #file.write_text(_)
    
    #def path(self, dir: Path,  name='maps') -> Path:
    #    return dir / f"{name}.obda"
