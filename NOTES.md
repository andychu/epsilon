Notes
=====

Other than parsing, biggest files are

    epsilon/
      # this is doing some smart-constructor-like stuff?
      regex.py - 248 lines
        regex nodes

      dfa.py - 119 lines 
        scan() runtime

      util.py - 170 lines
        IntegerSet - "An immutable set of integers, represented as sorted tuple
                      of disjoint, non-contiguous ranges."

cli.py has this parser:

            vector = dfa.ExpressionVector(
                    (token, parser.parse(section[token].replace("\n", "")))
                    for token in tokens)

## TODO

- Figure out why a?a?a?aaa is blowing up
- Write test harness / unit tests for ExpressionVector
  - do a JSON lexer I guess
- Add static typing
  - ExpressionVector might become separate


### Testing

- Testing:
  - ./run.sh nfa-suite
  - ./run.sh test-tool -- well there are no assertions here
  - ./backtrack.sh compare-syn-1 '' 20  -- bug to fix

### rsc-regexp

- Export NFAs to graphviz format -- compare "favorite regex" in NFA
- Fix `a**` bug

## Done

- Make a command line interface that's compatible with rsc-regexp
- Do the performance test for a?a?a?aaaa
  - compilation is very slow!
- Prune unused code and Refactor into functional style

## Understanding

- refactor from object-oriented style to functional style
  - e.g. the `derivative_classes()` method and so forth

  - but do we have a good test suite?
    - no, we only have `test_{parse,util}.py`

- TODO: OK let's write unit tests and shell tests for it!

- Maybe add some type anotations?

- see what we need for smart constructors

- maybe put things in fewer files


- Understand how it does unicode
  - is it iterating by byte, or by char?

- <https://archive.fosdem.org/2018/schedule/event/python_regex_derivatives/attachments/slides/2363/export/events/attachments/python_regex_derivatives/slides/2363/fosdem2018.pdf>


### Flow


- parse()
- dfa.construct()
- dfa.scan()

- Hm this algorithm is tiny
