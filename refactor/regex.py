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
import functools
import itertools
from . import util

from typing import Optional

cs = ((0, 0x10ffff), )

codespace = util.IntegerSet(cs)

#unicode = type("Regex", (object, ), locals())


@functools.total_ordering
class Expression:

    def __eq__(self, expr):
        return self._orderby() == expr._orderby()

    def __lt__(self, expr):
        return self._orderby() < expr._orderby()

    def __hash__(self):
        return hash(self._orderby())

    def __repr__(self):
        return "<{}>".format(str(self))

    def NullValue(self):
        return NULL


class SymbolSet(Expression):

    def __init__(self, codepoints=()):
        self._codepoints = util.IntegerSet(codepoints)
        if not codespace.issuperset(self._codepoints):
            raise ValueError("code point out of range")

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._codepoints or "")

    def _orderby(self):
        return self.__class__.__name__, self._codepoints

    @property
    def codepoints(self):
        return self._codepoints


class Epsilon(Expression):

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def _orderby(self):
        return self.__class__.__name__,


class KleeneClosure(Expression):

    def __new__(cls, expr):
        if isinstance(expr, KleeneClosure):
            return expr
        elif expr == EPSILON:
            return expr
        elif expr == NULL:
            return EPSILON

        self = super().__new__(cls)
        self._expr = expr
        return self

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._expr)

    def _orderby(self):
        return self.__class__.__name__, self._expr


class Complement(Expression):

    def __new__(cls, expr):
        if isinstance(expr, Complement):
            return expr._expr
        elif isinstance(expr, SymbolSet):
            return SymbolSet(codespace.difference(expr.codepoints))

        self = super().__new__(cls)
        self._expr = expr
        return self

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._expr)

    def _orderby(self):
        return self.__class__.__name__, self._expr

    def nu(self):
        nu = self._expr.nu()
        assert nu == EPSILON or nu == NULL
        return NULL if nu == EPSILON else EPSILON


class Concatenation(Expression):

    def __new__(cls, left, right):
        if isinstance(left, Concatenation):
            left, right = left._left, Concatenation(left._right, right)

        if left == NULL:
            return left
        elif right == NULL:
            return right
        elif left == EPSILON:
            return right
        elif right == EPSILON:
            return left

        self = super().__new__(cls)
        self._left = left
        self._right = right
        return self

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self._left,
                                   self._right)

    def _orderby(self):
        return self.__class__.__name__, self._left, self._right


class LogicalOr(Expression):

    def __new__(cls, left, right):
        if isinstance(left, SymbolSet) and isinstance(right, SymbolSet):
            return SymbolSet(left.codepoints.union(right.codepoints))

        terms = set()
        stack = [left, right]
        while stack:
            expr = stack.pop()
            if isinstance(expr, cls):
                stack.append(expr._left)
                stack.append(expr._right)
            elif expr == NULL:
                pass
            elif expr == SIGMA:
                return expr
            else:
                terms.add(expr)

        if not terms:
            return NULL

        new = super().__new__

        def construct(left, right):
            self = new(cls)
            self._left, self._right = left, right
            return self

        return functools.reduce(construct, sorted(terms, reverse=True))

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self._left,
                                   self._right)

    def _orderby(self):
        return self.__class__.__name__, self._left, self._right


class LogicalAnd(Expression):

    def __new__(cls, left, right):
        terms = set()
        stack = [left, right]
        while stack:
            expr = stack.pop()
            if isinstance(expr, cls):
                stack.append(expr._left)
                stack.append(expr._right)
            elif expr == NULL:
                return expr
            elif expr == SIGMA:
                pass
            else:
                terms.add(expr)

        if not terms:
            return SIGMA

        new = super().__new__

        def construct(left, right):
            self = new(cls)
            self._left, self._right = left, right
            return self

        return functools.reduce(construct, sorted(terms, reverse=True))

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self._left,
                                   self._right)

    def _orderby(self):
        return self.__class__.__name__, self._left, self._right


EPSILON = Epsilon()
SIGMA = SymbolSet(codespace)
NULL = SymbolSet()

# vim: sw=4
