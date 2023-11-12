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


class RegularVector(tuple):

    def __new__(cls, iterable):
        return super().__new__(cls, iterable)


@functools.total_ordering
class Expression:

    def __eq__(self, expr):
        return self._orderby() == expr._orderby()

    # Ordering is used to normalize OR / AND clauses.  See 2 sorted() call
    # below
    def __lt__(self, expr):
        return self._orderby() < expr._orderby()

    def __hash__(self):
        return hash(self._orderby())

    def __repr__(self):
        return "<{}>".format(str(self))


class SymbolSet(Expression):

    def __init__(self, codepoints=()):
        self._codepoints = util.IntegerSet(codepoints)
        if not codespace.issuperset(self._codepoints):
            raise ValueError("code point out of range")

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._codepoints or "")

    def _orderby(self):
        return self.__class__.__name__, self._codepoints


class Epsilon(Expression):

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def _orderby(self):
        return self.__class__.__name__,


class Star(Expression):
    _expr: Expression

    def __new__(cls, expr):
        if isinstance(expr, Star):
            return expr
        elif expr == EPSILON:
            return expr
        elif expr == EMPTY_SET:
            return EPSILON

        self = super().__new__(cls)
        self._expr = expr
        return self

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._expr)

    def _orderby(self):
        return self.__class__.__name__, self._expr


class Not(Expression):
    _expr: Expression

    def __new__(cls, expr):
        if isinstance(expr, Not):
            return expr._expr
        elif isinstance(expr, SymbolSet):
            return SymbolSet(codespace.difference(expr._codepoints))

        self = super().__new__(cls)
        self._expr = expr
        return self

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._expr)

    def _orderby(self):
        return self.__class__.__name__, self._expr


class Cat(Expression):
    _left: Expression
    _right: Expression

    def __new__(cls, left, right):
        if isinstance(left, Cat):
            left, right = left._left, Cat(left._right, right)

        if left == EMPTY_SET:
            return left
        elif right == EMPTY_SET:
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


class Or(Expression):
    _left: Expression
    _right: Expression

    def __new__(cls, left, right):
        if isinstance(left, SymbolSet) and isinstance(right, SymbolSet):
            return SymbolSet(left._codepoints.union(right._codepoints))

        terms = set()
        stack = [left, right]
        while stack:
            expr = stack.pop()
            if isinstance(expr, cls):
                stack.append(expr._left)
                stack.append(expr._right)
            elif expr == EMPTY_SET:
                pass
            elif expr == SIGMA:
                return expr
            else:
                terms.add(expr)

        if not terms:
            return EMPTY_SET

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


class And(Expression):
    _left: Expression
    _right: Expression

    def __new__(cls, left, right):
        terms = set()
        stack = [left, right]
        while stack:
            expr = stack.pop()
            if isinstance(expr, cls):
                stack.append(expr._left)
                stack.append(expr._right)
            elif expr == EMPTY_SET:
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
EMPTY_SET = SymbolSet()

# vim: sw=4
