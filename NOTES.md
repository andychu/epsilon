
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

- Make a command line interface that's compatible with rsc-regexp
  - Then all the same tests to see if they work
  - Is the syntax compatible?
    - well it uses ConfigParser, so NO
  - So I want an alternative front end -- borrow re2post, and make the infix
    nodes instead
    - or possibly just compile postfix to regex.py node types

