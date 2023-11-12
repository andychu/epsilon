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

import bisect
import collections
import itertools
import time
from . import regex
from . import util

log = util.log

Automaton = collections.namedtuple("Automaton",
                                   ["transitions", "accepts", "error"])


class ExpressionVector(tuple):

    def __new__(cls, iterable):
        return super().__new__(cls, iterable)

    def NullValue(self):
        return self.__class__((name, regex.NULL) for name, expr in self)

    def nullable(self):
        return [name for name, expr in self if expr.nullable()]

    def derivative(self, symbol):
        return ExpressionVector(
            (name, expr.derivative(symbol)) for name, expr in self)


def product_intersections(*sets):
    """Return the intersections of the cartesian product of sequences of sets.

    :param sets: Iterables sof sets.
    :return: A set of intersections.
    """
    return set(x[0].intersection(*x[1:]) for x in itertools.product(*sets))


def DerivClasses(state):
    #log('state %s', state)
    if isinstance(state, ExpressionVector):
        classes = (DerivClasses(expr) for _, expr in state)
        return filter(None, product_intersections(*classes))

    elif isinstance(state, regex.Epsilon):
        return {regex.codespace}

    elif isinstance(state, regex.SymbolSet):
        #raise AssertionError()
        return {
            state._codepoints,
            regex.codespace.difference(state._codepoints)
        }

    elif isinstance(state, regex.KleeneClosure):
        return DerivClasses(state._expr)

    elif isinstance(state, regex.Complement):
        return DerivClasses(state._expr)

    elif isinstance(state, regex.Concatenation):
        if state._left.nullable():
            return filter(
                None,
                product_intersections(DerivClasses(state._left),
                                      DerivClasses(state._right)))
        else:
            return DerivClasses(state._left)

    elif isinstance(state, regex.LogicalOr):
        return filter(
            None,
            product_intersections(DerivClasses(state._left),
                                  DerivClasses(state._right)))

    elif isinstance(state, regex.LogicalAnd):
        return filter(
            None,
            product_intersections(DerivClasses(state._left),
                                  DerivClasses(state._right)))

    else:
        raise AssertionError(state)
        #return state.derivative_classes()


def Derivative(state, symbol):
    #log('state %s', state)
    if isinstance(state, ExpressionVector):
        return ExpressionVector(
            (name, Derivative(expr, symbol)) for name, expr in state)

    elif isinstance(state, regex.Epsilon):
        return regex.NULL

    elif isinstance(state, regex.SymbolSet):
        return regex.EPSILON if state._codepoints.has(symbol) else regex.NULL

    elif isinstance(state, regex.KleeneClosure):
        return regex.Concatenation(Derivative(state._expr, symbol), state)

    elif isinstance(state, regex.Complement):
        return regex.Complement(Derivative(state._expr, symbol))

    elif isinstance(state, regex.Concatenation):
        return regex.LogicalOr(
            regex.Concatenation(Derivative(state._left, symbol), state._right),
            regex.Concatenation(state._left.nu(),
                                Derivative(state._right, symbol)))

    elif isinstance(state, regex.LogicalOr):
        return regex.LogicalOr(Derivative(state._left, symbol),
                               Derivative(state._right, symbol))

    elif isinstance(state, regex.LogicalAnd):
        return regex.LogicalAnd(Derivative(state._left, symbol),
                                Derivative(state._right, symbol))

    else:
        raise AssertionError(state)


def construct(expr):
    """Construct an automaton from a regular expression.

    :param expr: a regular expression or a ExpressionVector.
    :return: 
    """
    states = {expr: 0}
    transitions = [[]]

    start_time = time.time()
    i = 0

    stack = [expr]
    while stack:
        # DFA states correspond to regular languages derived from the
        # language we're compiling?
        state = stack.pop()
        number = states[state]

        # a?a has 4 states.  Linear in the size of the pattern
        log('number = %d', number)

        for derivative_class in DerivClasses(state):
            symbol = derivative_class[0][0]
            nextstate = Derivative(state, symbol)
            if nextstate not in states:
                states[nextstate] = len(states)
                transitions.append([])
                stack.append(nextstate)

            nextnumber = states[nextstate]
            for first, last in derivative_class:
                transitions[number].append((first, last, nextnumber))

                i += 1
                if i % 5 == 0:
                    #elapsed = time.time() - start_time
                    #util.log('%d iterations in %.5f seconds', i, elapsed)
                    pass

        transitions[number].sort()

    accepts = [state.nullable() for state in states]
    error = states[expr.NullValue()]
    return Automaton(transitions, accepts, error)


class NoMatchError(Exception):

    def __init__(self, atoms):
        msg = "No match for input {}".format(atoms)
        super().__init__(msg)


def scan(automaton, iterable, tosymbol=ord, pack=lambda atoms: "".join(atoms)):
    buffer, offset = [], 0
    state, accept, length = 0, False, 0
    atoms = iterable

    start_time = time.time()

    i = 0
    while True:
        if automaton.accepts[state]:
            accept = automaton.accepts[state]
            length = offset

        if offset < len(buffer):
            atom = buffer[offset]
        else:
            atom = next(atoms, None)
            if atom is not None:
                buffer.append(atom)

        if atom is not None:
            symbol = tosymbol(atom)
            transitions = automaton.transitions[state]

            # This is similar to util.IntegerSet.has(), but doesn't call it?
            i = bisect.bisect(transitions, (symbol, ))
            if i < len(transitions) and symbol == transitions[i][0]:
                state = transitions[i][2]
            elif i > 0 and (transitions[i - 1][0] <= symbol <=
                            transitions[i - 1][1]):
                state = transitions[i - 1][2]
            else:
                state = automaton.error
            offset += 1
        else:
            state = automaton.error

        if state == automaton.error:
            if accept:
                yield accept[0], pack(buffer[:length])
                buffer, offset = buffer[length:], 0
                state, accept, length = 0, False, 0

                # ANDY FIX: Prevents infinite loop
                break
            elif buffer:
                raise NoMatchError(buffer)
            else:
                break
        i += 1
        if i % 100 == 0:
            #elapsed = time.time() - start_time
            #util.log('%d iterations in %.5f seconds', 100, elapsed)
            pass


# vim: sw=4
