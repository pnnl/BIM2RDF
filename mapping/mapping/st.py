from typing import Annotated, Literal, NewType
from beartype.vale import *
from beartype import beartype

from abc import ABC, abstractmethod

# #Two = Annotated[int, IsEqual[2]]
# Two = Literal[2]

# Positive = Annotated[int, Is[lambda i: i>0]]

# #Adding = 

# class I(ABC): ...
# class O(ABC): ...

# class Adding(ABC):
#     @property
#     @abstractmethod
#     def a(self) -> int: ...
#     @property
#     @abstractmethod
#     def b(self) -> int: ...

#     @abstractmethod
#     def c(self) -> int: ...


#     def __call__(self, *args: Any, **kwds: Any) -> Any:
#         return super().__call__(*args, **kwds)


# @beartype
# def a1(n: Two) -> "lambda x: True":
#     return 'sdf'


# n(2)