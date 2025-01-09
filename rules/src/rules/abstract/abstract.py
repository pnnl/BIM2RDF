from abc import ABC, abstractmethod, abstractproperty
from typing import Iterable, Literal,  Any,  Iterator #, NoReturn
# from typing import Protocol do i need this?
from typing import Generic, TypeVar#, NewType, TypeVar

import sys
if sys.version_info >= (3, 11):
    from typing import Self as SelfT
else:
    from typing_extensions import Self as SelfT # need mypy > 1.0 (new)


SelfIterT = TypeVar('SelfIterT', bound='SelfIter',) # co/contravar matters?
class SelfIter(ABC, Generic[SelfIterT]):
    @abstractmethod
    def __iter__(self) -> Iterator[SelfIterT]:
        ...

DataType = TypeVar('DataType',     bound='Data')
DataBaseType = TypeVar('DataBaseType', bound='DataBase')
class Data(ABC, Generic[DataBaseType], ):#Datum(ABC):

    @abstractmethod
    def __add__(self, data: SelfT) -> SelfT: # or Self -> Self?
        ...


# dont even need to talk about an iterable here
#class Iterable
#Data = Iterable[Datum] # that's right! data (the word) is plural. there ARE data!
# stuff that's commented out can be abstract/triples

class DataBase(ABC):#, Generic[DataBaseType, ]):
    ...
    #@abstractmethod
    #def __iter__(self) -> Data:
    #    ...

    #@abstractmethod
    #def query(self, query: QueryType ) -> Data: # db has the chance to give back a 'ref' to its internal results
    #    ...
    
    #@abstractmethod
    #def insert(self, data: Data) -> None: # NoReturn the same thing?
    #    ...

QueryType = TypeVar('QueryType', bound='Query')
class Query(ABC, Generic[QueryType, DataBaseType] ):

    #@abstractmethod not needed in the abstraction but suggested
    #def __str__(self) -> str:
    #    ...

    @abstractmethod
    def __add__(self, query: QueryType) -> QueryType:
    # should be doable
        ...

    @abstractmethod
    def __call__(self, db: DataBaseType) -> Data:
        ...

RuleType = TypeVar('RuleType', bound='Rule')
class Rule(ABC, Generic[DataBaseType, DataType]): # mapping?

    @abstractproperty  #could remove
    def spec(self)    -> Any:
        ...

    @abstractmethod
    def __add__(self, rule: SelfT) -> 'Rules':
        # should be able to add rules to get a new rule
        ...
            
    @abstractmethod
    def meta(self, data: DataType) -> Data: # data: Data and -> Data dont have to be the same
        ...

    @abstractmethod
    def __call__(self, db: DataBaseType) -> Data: # like a 'diff'
        # so any metadata insertion into the db can be handled here
        ...

RulesType = TypeVar('RulesType', bound='Rules')
class Rules(Rule, SelfIter, ABC):
    ... # does iterable imply iterable of rules?


class Validation(ABC):

    @abstractproperty
    def spec(self)    -> Any:
        ...

    @abstractmethod
    def __add__(self) -> 'Validation':
        ...
    
    @abstractmethod
    def __call__(self, db: DataBase) -> 'Result':
        ...

class Validations(Validation, SelfIter, ABC):
    ...


Success = Literal[True]
Failure = Literal[False]
#Result = Success | Failure complaint

class Result:
    @abstractproperty
    def db(self) -> DataBase:
        ...
    @abstractmethod
    def __bool__(self) -> Success | Failure:
        ...
    @abstractmethod
    def __call__(self,) -> Any:
        ...

class Engine(ABC):

    @abstractproperty
    def rules(self) -> Rule | Rules:
        ...
    
    @abstractproperty # needed?
    def db(self) -> DataBase:
        ...

    @abstractmethod
    def validate(self) -> Result:
        ...

    @abstractmethod
    #def __call__(self, db: DataBase) -> Result:
    def __call__(self) -> Result:
        ...


#class Validation(Result, ABC):
    #...


