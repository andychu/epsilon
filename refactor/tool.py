# Alternative to cli.py that matches our test interface

import os
import sys
import time

from . import dfa
from . import parse
from . import regex
from . import util


def log(msg, *args):
    if 1:
        util.log(msg, *args)


def main(argv):
    pat = argv[1]
    s = argv[2]

    start_time = time.time()

    parser = parse.Parser()

    try:
        expr = parser.parse(pat)
    except parse.SyntaxError as e:
        #print(e)
        print('bad regexp')  # the common protocol
        return

    elapsed = time.time() - start_time
    log('\t%.5f Parsed', elapsed)

    #log(expr)

    name = 'main'
    # Singleton
    vector = regex.ExpressionVector([(name, expr)])
    #log(vector)

    automaton = dfa.construct(vector)

    elapsed = time.time() - start_time
    log('\t%.5f DFA', elapsed)

    #log(automaton)
    #log('')
    #log('A0 %s', automaton[0])

    #target = target_execute.Target(s)
    #target.emit_automaton(name, automaton)

    #text = (c for line in sys.stdin for c in line)
    #print(list(text))

    # Must be an iterator

    text = iter(s)

    # TODO:  need two modes
    # - anchored match
    # - findall() for lexer
    # - add tests to catch unanchored

    try:
        for token, match in dfa.scan(automaton, text):
            #print(token, repr(match))
            print(match)
    except dfa.NoMatchError:
        print('NOPE')

    log('\t%.5f Matched', elapsed)

    if 0:
        pid = os.getpid()
        log('PID %d sleep', pid)
        os.system('cat /proc/%d/status' % pid)
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv)
