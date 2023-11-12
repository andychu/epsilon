import itertools
import random
import unittest
import time
from . import dfa
from . import parse
from . import regex
from . import util

log = util.log


class TestDfa(unittest.TestCase):

    def testLexer(self):
        parser = parse.Parser()
        lexer = [
            ('string', r'"([^\"]|\\.)*"'),
            ('number', r'[0-9]+'),
            ('identifier', r'[a-zA-Z][a-zA-Z0-9]+'),
            ('whitespace', r'[ ]+'),
        ]
        vector = regex.RegularVector([(name, parser.parse(pat))
                                      for name, pat in lexer])
        print(vector)
        automaton = dfa.construct(vector)

        text = iter('99 hello "there" 42 foo99')
        for token, match in dfa.scan(automaton, text):
            print(token, repr(match))

    def testBacktracking(self):
        n = 32
        #n = 2

        pat = 'a?' * n + 'a' * n
        log('PAT %s', pat)

        parser = parse.Parser()

        expr = parser.parse(pat)
        log('EXPR %s', expr)
        log('')

        vector = regex.RegularVector([('main', expr)])
        #print(vector)

        start_time = time.time()
        #automaton = dfa.construct(vector)

        d = dfa.Derivative(expr, ord('a'))

        log('DERIV %s', d)
        log('')

        elapsed = time.time() - start_time
        log('n = %d, elapsed %.3f ms', n, elapsed * 1000)

        # Does not seem slow
        # Is Nu() slow?

        start_time = time.time()
        nu = dfa.Nu(expr)

        log('Nu %s', nu)
        log('')

        elapsed = time.time() - start_time
        log('n = %d, elapsed %.3f ms', n, elapsed * 1000)



if __name__ == '__main__':
    unittest.main()
