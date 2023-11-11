# Epsilon
# Copyright (C) 2018
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

from . import target
from . import version

class Target(target.Target):
    def emit_header(self):
        print("// This file was generated by Epsilon {}".format(
                version.VERSION))

    def emit_automaton(self, name, automaton):
        print("digraph {} {{".format(name))
        for state, edges in enumerate(automaton.transitions):
            for first, last, nextstate in edges:
                print("    state{} -> state{}[label=\"({},{})\"];".format(
                        state, nextstate, first, last))
            accepts = automaton.accepts[state]
            if accepts:
                print("    state{}[label=\"{}\", peripheries=2];".format(
                        state, accepts[0]))

        print("    state{}[label=\"error\", shape=box];".format(
                automaton.error))
        print("}")
