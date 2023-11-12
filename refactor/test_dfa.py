import itertools
import random
import unittest
from . import dfa
from . import parse
from . import regex
from . import util


class TestDfa(unittest.TestCase):

    def test_lexer(self):
        parser = parse.Parser()
        lexer = [
            ('string', r'"([^\"]|\\.)*"'),
            ('number', r'[0-9]+'),
            ('identifier', r'[a-zA-Z][a-zA-Z0-9]+'),
            ('whitespace', r'[ ]+'),
        ]
        vector = regex.ExpressionVector([(name, parser.parse(pat))
                                         for name, pat in lexer])
        print(vector)
        automaton = dfa.construct(vector)

        text = iter('99 hello "there" 42 foo99')
        for token, match in dfa.scan(automaton, text):
            print(token, repr(match))


if __name__ == '__main__':
    unittest.main()
