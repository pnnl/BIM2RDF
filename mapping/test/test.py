#%%
#%load_ext autoreload
#%autoreload 2
#from mapping import mapping_dir
#test_dir = 
from pathlib import Path
import mapping.mapping as m

test_dir = Path(__file__).parent


sr = m.SQLRDFMapping.from_args('test', 'brick', m.SQLiteDB(test_dir / 'test.sqlite') )

sr.ontology.graph
#_ = m.DBProperties.make(Path('test.sqlite'))
#_ = m.OntopProperties.make()
#_ = m.Mapping.make()
#_ = m.SQLRDFMap.make('reference-223p')
#from attr import asdict
#_ = asdict(_)

#print( str(_) )

# import mapping as m
# s = """CREATE TABLE "Wires" ("Id" integer, "TypeId" integer, "PhaseCreated" integer, "PhaseDemolished" integer, "DesignOption" integer, "CircuitDescription" wvarchar(255), "CircuitLoadName" wvarchar(255), "NumberofConductors" integer, "TickMarks" wvarchar(255), "Panel" wvarchar(255), "Circuits" wvarchar(255), "Type" wvarchar(255), "HotConductors" integer, "NeutralConductors" integer, "GroundConductors" integer, "WireSize" wvarchar(255), "IfcGUID" wvarchar(255), "Comments" wvarchar(255), "Mark" wvarchar(255), CONSTRAINT "CWires" PRIMARY KEY ("Id"))"""
# from pathlib import Path
# f = Path('test.sqlite')
# m.DBProperties.sqlite(f)
# #%%
# from abc import ABC, abstractmethod
# from typing import Literal, overload

# class _B(ABC):
#     @property
#     @abstractmethod
#     def a(self) -> int: ...
#     @property
#     @abstractmethod
#     def const(self) -> Literal[3]: ...

#     @overload
#     @abstractmethod
#     def f(self, x: int) -> str: ...
#     @overload
#     @abstractmethod
#     def f(self, x: str) -> str: ...
    
#     def f(self, x: str| int) -> str: ...


# from attrs import frozen as dataclass
# @dataclass
# class B(_B):
#     a: int
#     #@property
#     #def const(self) -> Literal[3]: return 3
#     const: Literal[3]
#     #@overload
#     #def f(x: str) -> str: ...
#     @overload
#     def f(self, x: int) -> str: ...
#     @overload
#     def f(self, x: bool) -> str: ...
    
#     def f(self, x: bool | int) -> str: ...

# print(B(3).const)



# if 0:
#     class TestAbs(Base):
#         #@property
#         #@abstractmethod
#         #def attr(self): ...
#         attr: str
#     from attrs import frozen as dataclass
#     @dataclass
#     class TestImpl(TestAbs):
#         attr: str
#         @classmethod
#         def make(cls):
#             return cls(5)
#     print(TestImpl.make())
#     exit()

#     class BaseC(ABC):
#         @property
#         @abstractmethod
#         def myconst(self) -> int: ...

#     @dataclass
#     class C(BaseC):
#         #@property
#         #def myconst(self) -> Literal[3]
#         #myconst: int
#         @property
#         def myconst(self) -> int: return 'ssdfs'

#     BaseC()
#     print(C())

