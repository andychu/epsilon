# Alternative to cli.py that matches our test interface

import configparser
import os
import re
import sys
import time

from . import dfa
from . import parse
from . import regex
from . import util


def log(msg, *args):
    if 1:
        util.log(msg, *args)


class _Interpolation(configparser.Interpolation):
    _re_braces = re.compile(r"(\{[^}]*})"
                            r"|\\\{"
                            r"|\{[0-9]+(,[0-9]*)}"
                            r"|\\[opPx]\{[^}]*}")

    def before_get(self, parser, section, option, value, defaults):
        return self._interpolate(parser, section, option, value, set())

    def _interpolate(self, parser, section, option, value, seen):
        fragments = []
        offset = 0
        while offset < len(value):
            match = self._re_braces.search(value, offset)
            if match:
                start, end = match.span()
                if match.group(1):
                    name = value[start + 1:end - 1]
                    if name in seen:
                        raise configparser.InterpolationError(
                            name, section,
                            "{}: interpolation loop detected".format(name))
                    interpolated = parser.get(section,
                                              name,
                                              raw=True,
                                              fallback=None)
                    if interpolated is None:
                        raise configparser.InterpolationMissingOptionError(
                            option, section, value, name)
                    fragments.append(value[offset:start])
                    fragments.append(
                        self._interpolate(parser, section, name, interpolated,
                                          seen.union({name})))
                    offset = end
                else:
                    fragments.append(value[offset:end])
                    offset = end
            else:
                fragments.append(value[offset:])
                break

        return "".join(fragments)


def main(argv):
    action = argv[1]

    if action == 'match':
        pat = argv[2]
        s = argv[3]

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

        log(expr)

        name = 'main'
        # Singleton
        vector = regex.RegularVector([(name, expr)])
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
                # Print one match
                break
        except dfa.NoMatchError:
            print('NOPE')

        log('\t%.5f Matched', elapsed)

    elif action == 'lex':

        config = configparser.ConfigParser(interpolation=_Interpolation())
        config.optionxform = str
        with open(argv[2]) as f:
            config.read_file(f)

        for name in config.sections():  # Should only be one section
            section = config[name]
            parser = parse.Parser()
            tokens = tuple(key for key in section if not key.startswith("_"))
            assert len(tokens) > 0
            if 0:
                for token in tokens:
                    pat = section[token]
                    parsed = parser.parse(pat.replace('\n', ''))

                    print('T', token)
                    print('PAT', pat)
                    print('PARSED', parsed)

            vector = regex.RegularVector(
                (token, parser.parse(section[token].replace("\n", "")))
                for token in tokens)
            automaton = dfa.construct(vector)

            log('automaton %s', automaton)

            s = sys.stdin.read()
            try:
                for token, match in dfa.scan(automaton, iter(s)):
                    print(token, repr(match))
            except dfa.NoMatchError:
                print('NOPE')

    else:
        raise RuntimeError('Invalid action %r' % action)

    if 0:
        pid = os.getpid()
        log('PID %d sleep', pid)
        os.system('cat /proc/%d/status' % pid)
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv)
