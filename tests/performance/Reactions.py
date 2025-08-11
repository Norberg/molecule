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
import unittest
from libcml import Cml
from libcml import CachedCml
from libreact.Reaction import Reaction
from libreact.Reactor import sublist_in_list
from libreact.Reactor import Reactor
import time

def setupRealReactor():
    cml = Cml.Reactions()
    cml.parse("data/reactions")
    reactor = Reactor(cml.reactions)
    return reactor

def performance_test(times):
    reactor = setupRealReactor()
    for x in range(times):
        reaction = reactor.react(["CH4(g)", "H2O(g)"], K=1000)
        if not reaction.products == ["CO(g)", "H2(g)", "H2(g)", "H2(g)"]:
            raise Exception("Test did not return expected value, got", reaction.products)


if __name__ == "__main__":
    NR_OF_TIMES = 1000
    start = time.time()
    performance_test(NR_OF_TIMES)
    end = time.time()
    total_time = end - start
    print("Exectude: ", NR_OF_TIMES ,"times in", total_time , "seconds")
