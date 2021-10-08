from __future__ import annotations

from abc import abstractmethod, ABC
from collections.abc import Set
from typing import TypeVar, Generic, Iterator, Dict, MutableSet


class Identifier(ABC):
    def __init__(self, identifier: str):
        self.identifier = identifier

    def __eq__(self, other):
        return isinstance(other, Identifier) and \
               self.get_domain() == other.get_domain() and \
               self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    @abstractmethod
    def get_domain(self) -> str:
        pass

    def __repr__(self):
        return f'ID: {self.get_domain()}/{self.identifier}'


E = TypeVar("E", bound=Identifier)


class IdentifierSet(Generic[E], MutableSet):
    # TODO: this is wrong, should probably just be Set[E]
    def __init__(self, items: MutableSet[E]):
        self.items: MutableSet[E] = items

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[E]:
        # return iter(self.items)
        # return self.items.__iter__()
        for i in self.items:
            yield i

    def __contains__(self, x: object) -> bool:
        return isinstance(x, Identifier) and x in self.items

    def add(self, value: E) -> None:
        self.items.add(value)

    def discard(self, value: E) -> None:
        self.items.discard(value)

    # TODO OPT: find a way to do this via hash, rather than iteration
    def __getitem__(self, identifier: Identifier) -> E:
        return next(item for item in self.items if item == identifier)


class Asdf(Identifier):
    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return str(self.identifier)

    def get_domain(self) -> object:
        return "asdf_domain"
