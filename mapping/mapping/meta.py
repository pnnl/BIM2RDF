from typing import TypeVar
from typing import Iterable
from typing import Generic, Any
from typing import final
from abc import ABC as _ABC,  abstractmethod
from typing import Protocol, runtime_checkable


T = TypeVar('T', covariant=True)
@runtime_checkable
class ClassIterator(Generic[T], Protocol):
    @classmethod
    @abstractmethod
    def s(cls, frm: Any) -> Iterable[T]:
        raise NotImplementedError

@runtime_checkable
class Validation(Generic[T], Protocol):
    @abstractmethod
    def validate(self) -> bool:
       """arbitrary validations. mainly want to assert invariants."""
       raise NotImplementedError


class Construction(Generic[T], Validation[T]):
    @classmethod
    @abstractmethod
    def make(cls, frm: Any) -> T:
    #https://github.com/python/mypy/issues/5876
        raise NotImplementedError
                                

    @final
    @classmethod
    def __init_subclass__(cls, *p, spec_cls_idx=0, validate: bool=True, impl: bool | None=None, **k):
        super().__init_subclass__(*p, **k)

        def infer_impl(cls) -> bool | None:
            if cls.__name__ in {c.__name__ for c in cls.__bases__}:
                return True
            else: return False
            return None
        
        # so lean towards the programmer having to be explicit.
        if (infer_impl(cls) is None) and (impl is None):
            raise NotImplementedError(f'is {cls} an abstraction or implementation ?')
        
        impl = impl or infer_impl(cls) # prefer impl over what was inferred
        if impl:
            if cls.__name__ != cls.__bases__[spec_cls_idx].__name__:
                raise NameError("use same name as in 'schema' ")
            

            def post_init(self): # the impl

                # not in metaland
                if validate:
                    # metabases: 
                    # self.__class__.__bases__[0]...: the metaclass that you're trying to implement
                    # ....__bases__:                  the bases of the metaclass
                    metabases = list(b for b in self.__class__.__bases__[spec_cls_idx].__bases__ if  b.__module__ != __name__ ) # ...exluding metaclasses in this file
                    for bc in [self.__class__]+list(metabases):
                        if hasattr(bc, 'validate'):
                            if not bc.validate(self):
                                raise TypeError(f'{bc} of {repr(self)} invalid')

            # this is actually an implementation detail
            # but i didn't know how to have a generic post_init
            cls.__attrs_post_init__ = post_init # type: ignore

#              adding 'construction' although i think it's an implementation 
#              ....saves adding 
class ABC(_ABC,  Construction): ... 
