# Alternative to cli.py that matches our test interface

import sys

from . import dfa
from . import parse
from . import target_execute


def log(msg, *args):
    if 0:
        if args:
            msg = msg % args
        print(msg, file=sys.stderr)


def main(argv):
    pat = argv[1]
    s = argv[2]

    parser = parse.Parser()

    try:
        expr = parser.parse(pat)
    except parse.SyntaxError as e:
        #print(e)
        print('bad regexp')  # the common protocol
        return 

    log(expr)

    name = 'main'
    # Singleton
    vector = dfa.ExpressionVector([(name, expr)])
    log(vector)

    automaton = dfa.construct(vector)

    log(automaton)
    log('')
    log('A0 %s', automaton[0])

    #target = target_execute.Target(s)
    #target.emit_automaton(name, automaton)

    #text = (c for line in sys.stdin for c in line)
    #print(list(text))

    # Must be an iterator
    text = iter(s)
    log(text)

    try:
        for token, match in dfa.scan(automaton, text):
            #print(token, repr(match))
            print(match)
    except dfa.NoMatchError:
        print('NOPE')



if __name__ == '__main__':
    main(sys.argv)
