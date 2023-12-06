import itertools
import random
import unittest
import string
import sys
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

    # Set before main()
    NUM_ALTS = 5

    def testManyAlternates(self):
        parser = parse.Parser()
        #print(dir(string))

        lexer = []
        for c in string.ascii_letters:
            lexer.append((c, c * 10))
        #print(lexer)

        log('N = %d', self.NUM_ALTS)

        # This blows up too!  So it's not just concatenation, but also
        # alternation.
        lexer = lexer[:self.NUM_ALTS]

        vector = regex.RegularVector([(name, parser.parse(pat))
                                      for name, pat in lexer])
        #print(vector)
        automaton = dfa.construct(vector)

    def testBacktracking(self):
        n = 40
        #n = 2

        # Original rsc test case
        #pat = 'a?' * n + 'a' * n

        # This doesn't repro the bug
        #pat = 'a' * n

        # Enough to repro the bug
        pat = 'a?' * n

        log('PAT %s', pat)

        parser = parse.Parser()

        expr = parser.parse(pat)

        if 0:
            log('EXPR %s', expr)
            log('')

        vector = regex.RegularVector([('main', expr)])
        #print(vector)

        start_time = time.time()

        # This can blow up even more
        #automaton = dfa.construct(vector)

        # This also blows up
        d = dfa.Derivative(expr, ord('a'))

        if 0:
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
    if len(sys.argv) > 1:
        TestDfa.NUM_ALTS = int(sys.argv.pop())

    unittest.main()
