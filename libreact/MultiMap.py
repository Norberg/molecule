# Molecule - a chemical reaction puzzle game
# Copyright (C) 2014 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations

from typing import Callable, Generic, Iterable, TypeVar, overload

K = TypeVar("K")
V = TypeVar("V")
E = TypeVar("E")


class MultiMapEntry(Generic[K, V]):
    def __init__(self, keys: Iterable[K], value: V) -> None:
        self.keys = keys
        self.value = value


class MultiMap(Generic[K, V, E]):
    @overload
    def __init__(
        self,
        entries: Iterable[MultiMapEntry[K, V]],
        entry_mapper: None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        entries: Iterable[E],
        entry_mapper: Callable[[E], MultiMapEntry[K, V]],
    ) -> None: ...

    def __init__(
        self,
        entries: Iterable[object],
        entry_mapper: Callable[[E], MultiMapEntry[K, V]] | None = None,
    ) -> None:
        self.multi_map: dict[K, list[V]] = {}
        for e in entries:
            if entry_mapper is None:
                if not isinstance(e, MultiMapEntry):
                    raise TypeError("MultiMap entries must be MultiMapEntry when entry_mapper is None")
                entry = e
            else:
                entry = entry_mapper(e)
            self.add_entry(entry)

    def add_entry(self, entry: MultiMapEntry[K, V]) -> None:
        for key in entry.keys:
            if key in self.multi_map:
                self.multi_map[key].append(entry.value)
            else:
                self.multi_map[key] = [entry.value]

    def __getitem__(self, key: K) -> list[V]:
        return self.multi_map[key]
