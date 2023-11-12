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
from dataclasses import dataclass
import itertools
import time
from . import regex
from . import util

from typing import Set, Dict, List, Tuple, Any, Optional, Union

log = util.log


@dataclass
class Automaton:
    transitions: List[List[Tuple[int, int, int]]]
    accepts: List[List[str]]
    error: int


def product_intersections(sets):
    """Return the intersections of the cartesian product of sequences of sets.

    :param sets: Iterables sof sets.
    :return: A set of intersections.
    """
    # intersection() method accepts multiple
    return set(x[0].intersection(*x[1:]) for x in itertools.product(*sets))
    """
    result = set()
    for x in itertools.product(*sets):
        result.add(x[0].intersection(*x[1:]))
    return result
    """


def ProductIntersect(a: util.IntegerSet, b: util.IntegerSet):
    return set(
        left.intersection(right) for left, right in itertools.product(a, b))


def DerivClasses(state: regex.Expression):
    #log('state %s', state)
    if isinstance(state, regex.RegularVector):
        classes = (DerivClasses(expr) for _, expr in state)
        return filter(None, product_intersections(classes))

    elif isinstance(state, regex.Epsilon):
        return {regex.codespace}

    elif isinstance(state, regex.SymbolSet):
        return {
            state._codepoints,
            regex.codespace.difference(state._codepoints)
        }

    elif isinstance(state, regex.KleeneClosure):
        return DerivClasses(state._expr)

    elif isinstance(state, regex.Complement):
        return DerivClasses(state._expr)

    elif isinstance(state, regex.Concatenation):
        if Nullable(state._left):
            return filter(
                None,
                ProductIntersect(DerivClasses(state._left),
                                 DerivClasses(state._right)))
        else:
            return DerivClasses(state._left)

    elif isinstance(state, regex.LogicalOr):
        return filter(
            None,
            ProductIntersect(DerivClasses(state._left),
                             DerivClasses(state._right)))

    elif isinstance(state, regex.LogicalAnd):
        return filter(
            None,
            ProductIntersect(DerivClasses(state._left),
                             DerivClasses(state._right)))

    else:
        raise AssertionError(state)
        #return state.derivative_classes()


def Derivative(state: regex.Expression, symbol: str):
    #log('state %s', state)
    if isinstance(state, regex.RegularVector):
        return regex.RegularVector(
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
            regex.Concatenation(Nu(state._left),
                                Derivative(state._right, symbol)))

    elif isinstance(state, regex.LogicalOr):
        return regex.LogicalOr(Derivative(state._left, symbol),
                               Derivative(state._right, symbol))

    elif isinstance(state, regex.LogicalAnd):
        return regex.LogicalAnd(Derivative(state._left, symbol),
                                Derivative(state._right, symbol))

    else:
        raise AssertionError(state)


def Nullable(state: regex.Expression):
    if isinstance(state, regex.RegularVector):
        return [name for name, expr in state if Nullable(expr)]
    else:
        nu = Nu(state)
        assert nu == regex.EPSILON or nu == regex.NULL
        return nu == regex.EPSILON


def Nu(state: regex.Expression):
    if isinstance(state, regex.Epsilon):
        return state

    elif isinstance(state, regex.SymbolSet):
        return regex.NULL

    elif isinstance(state, regex.KleeneClosure):
        return regex.EPSILON

    elif isinstance(state, regex.Complement):
        nu = Nu(state._expr)
        assert nu == regex.EPSILON or nu == regex.NULL
        return regex.NULL if nu == regex.EPSILON else regex.EPSILON

    elif isinstance(state, regex.Concatenation):
        return regex.LogicalAnd(Nu(state._left), Nu(state._right))

    elif isinstance(state, regex.LogicalOr):
        return regex.LogicalOr(Nu(state._left), Nu(state._right))

    elif isinstance(state, regex.LogicalAnd):
        return regex.LogicalAnd(Nu(state._left), Nu(state._right))

    else:
        raise AssertionError(state)


def construct(expr: Any) -> Automaton:
    """Construct an automaton from a regular expression.

    :param expr: a regular expression or a RegularVector.
    :return: 
    """
    states: Dict[Any, int] = {expr: 0}
    transitions: List[List[Tuple[int, int, int]]] = [[]]

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

        for deriv_class in DerivClasses(state):
            symbol = deriv_class[0][0]
            nextstate = Derivative(state, symbol)
            if nextstate not in states:
                states[nextstate] = len(states)
                transitions.append([])
                stack.append(nextstate)

            nextnumber = states[nextstate]
            for first, last in deriv_class:
                transitions[number].append((first, last, nextnumber))

                i += 1
                if i % 5 == 0:
                    #elapsed = time.time() - start_time
                    #util.log('%d iterations in %.5f seconds', i, elapsed)
                    pass

        transitions[number].sort()

    accepts = [Nullable(state) for state in states]

    assert isinstance(expr, regex.RegularVector)

    # Null value for "regular vector" from paper
    null_value = regex.RegularVector(
        (name, regex.NULL) for name, expr in state)

    # Should this be called "error" or something else?
    error_num = states[null_value]
    return Automaton(transitions, accepts, error_num)


class NoMatchError(Exception):

    def __init__(self, atoms):
        msg = "No match for input {}".format(atoms)
        super().__init__(msg)


def scan(automaton: Automaton, atoms):
    buffer: List[str] = []  # Optional because of None
    offset = 0

    state = 0
    accept = None  # TODO: Is this a state?
    accept_pos = 0

    start_time = time.time()

    j = 0
    while True:
        if automaton.accepts[state]:
            accept = automaton.accepts[state]
            accept_pos = offset

        if offset < len(buffer):
            atom = buffer[offset]
        else:
            atom = next(atoms, None)  # type: ignore
            if atom is not None:
                buffer.append(atom)

        #log('\t%d. offset %d   atom %r  buffer %r', j, offset, atom, buffer)

        if atom is not None:
            symbol = ord(atom)
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
                yield accept[0], ''.join(buffer[:accept_pos])

                buffer = buffer[accept_pos:]
                # It's NOT empty after truncation!
                # log('\tbuf %r', buffer)

                offset = 0
                state = 0
                accept = None

            elif buffer:  # unmatched in buffer
                raise NoMatchError(buffer)

            else:
                break
        j += 1
        if j % 100 == 0:
            #elapsed = time.time() - start_time
            #util.log('%d iterations in %.5f seconds', 100, elapsed)
            pass


# vim: sw=4
