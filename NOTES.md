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
  - is the existing canonicalization OK, or do we need a new approach?
  - it's based on tuples.  Maybe write some unit tests

- Add static typing
  - ExpressionVector might become separate
  - canonicalization seems like an issue

  - IntegerSet is tuple
  - RegularVector is tuple

  - I kinda want to be Expression with values

## Questions

- Can we accept that `a?a?a? ... aaa ...` blows up at compile time?
  - Because that regex has a high amount of "non-determinism"
- But maybe most **common** regexes don't have this?
  - So derivatives are good for a lexer generator, but not user-defined regexes?
  - That's my current theory, based on some hacking, but I haven't seen this claim in practice.

- ANSWER: A lexer with MANY expressions also blows up.  It's not just LONG ones.
  - I think this is inherent in the "regex with derivatives" algorithm.
  - Did the original paper not mention this?

So then I think it would be IMPRACTICAL to export the whole Oils lexer to this
tiny algorithm.

I guess this was obvious from the start, but I thought some of the
canonicalization or maybe hash-consing would do some magic.

### Testing

- Testing:
  - ./run.sh nfa-suite
  - ./run.sh test-tool -- well there are no assertions here
  - ./backtrack.sh compare-syn-1 '' 20  -- bug to fix

### rsc-regexp

- Export NFAs to graphviz format -- compare "favorite regex" in NFA
- Fix `a**` bug

Markdown/blog:

- add timing of NFA vs. backtracking node.js
  - add note that I couldn't repro cloudflare issue.  Theory: it's capturing
  - I think their explanation of Perl 5 RegexpDebugger is simply wrong -- it's
    an overly naive view of PCRE.

- Add note that I made "my favorite" regex work

## Done

- Make a command line interface that's compatible with rsc-regexp
- Do the performance test for a?a?a?aaaa
  - compilation is very slow!
- Prune unused code and Refactor into functional style
- Write test harness / unit tests for ExpressionVector
  - do a JSON lexer I guess

## Understanding

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
