from multiprocessing.sharedctypes import Value
from phantom import Predicate
from . import mapping_dir
from typing import Iterator, Callable
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


class ShortName(str, Phantom, predicate=lambda s: 'jdbc' not in s): ...

# implementations

from attrs import frozen as dataclass

@dataclass
class DBProperty(s.DBProperty):
    name:   s.DBPropertyName
    value:  str
    @classmethod
    def make(cls, *p, **k): return cls._make(p[0], p[1])
    @classmethod
    def _make(cls, short_name: ShortName, value: str) -> 'DBProperty':
        return cls(s.DBPropertyName(f"jdbc.{short_name}"), value)

    def __str__(self) -> s.PropertyStr:
        return s.PropertyStr(f"{self.name}={self.value}")


@dataclass
class DBProperties(s.DBProperties):
    name:   DBProperty
    url:    DBProperty
    driver: DBProperty
    user:   DBProperty
    
    @classmethod
    # *p, **k pleases mypy
    def make(cls, *p, **k) -> 'DBProperties':
        return cls.sqlite(*p, **k)

    @classmethod
    def sqlite(cls, file: SQLiteDB) -> 'DBProperties':
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
    def constraint_stripper(cls, sqlitedb: PathStr | Path )-> Iterator[str]:
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

class OntopProperties:#(s.OntopProperties):

    def lines(self):
        from attrs import asdict
        _ = asdict(self)
        return properties_lines(_)


class Properties:#(s.Properties):

    def lines(self) -> Iterator[str]:
        from attrs import asdict
        for k,v in asdict(self, recurse=False).items():
            for line in v.lines():
                yield f"{k}.{line}" # just prefix

    def write(self, file):
        file.writelines(self.lines())

    def path(self, dir: Path,  name='sql') -> Path:
        return dir / f"{name}.properties"

class Mapping:#(dict, s.Mapping,):

    @classmethod
    def from_yamlfile(cls, path: Path) -> 'Mapping':
        import yaml
        return cls(**yaml.safe_load(open(path)))

    @classmethod
    def from_name(cls, name) -> 'Mapping':
        return cls(**cls.from_yamlfile(mapping_dir / name))
        
    def make_obda(self: dict) -> str:
        from jinja2 import Environment, FileSystemLoader#, select_autoescape
        env = Environment(loader=FileSystemLoader(mapping_dir))

        def strip_comments(lines):
            lines = lines.split('\n')
            o = ""
            for ln in lines:
                o += ln.split('#', 1)[0]
                o += ' ' # need a lil space sometimes
            return o
        for map in self['maps']:
            map['target'] = strip_comments(map['target'])
            map['source'] = strip_comments(map['source'])
        return env.get_template('obda.jinja').render(**self)

    
    def write(self, file):
        _ = self.make_obda()
        file.writelines(file)

    
    def path(self, dir: Path,  name='maps') -> Path:
        return dir / f"{name}.obda"


def get_workspace(loc: Path= mapping_dir / 'work') -> Path:
    if not loc.exists():
        loc.mkdir()
    else:
        from shutil import rmtree
        rmtree(loc)
        loc.mkdir()
    return loc



class Ontology:#(s.Ontology):
    
    @classmethod
    def from_name(cls, onto_name) -> 'Ontology':
        from ontologies import get
        _ =  get(onto_name)
        _ = cls(onto_name, _)
        return _

    def write(self, file):
        self.graph.serialize(file, format='turtle')
    
    def path(self, dir: Path,  name='onto'):
        return dir / f"{name}.ttl"

class OntologyCustomization:#(s.OntologyCustomization):

    @classmethod
    def from_name(cls, name: str) -> Callable[[str], 'OntologyCustomization']:
        return partial(cls, ontology=Ontology.from_name(name))

    
    @property
    def graph(self) -> s.Graph:
        def turtle_soup(loc):
            g = s.Graph()
            for f in (f for f in ( loc ).iterdir() if f.suffix == '.ttl'):
                g += s.Graph().parse(f)
            return g
        # do something with building TODO
        return turtle_soup( mapping_dir / self.ontology.name )

    def write(self, file):
        self.graph.serialize(file, format='turtle')
        

class SQLRDFMap:#(s.SQLRDFMap):

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


