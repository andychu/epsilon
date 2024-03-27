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

## Testing

Commands:

- `./run.sh test-tool`
  - Runs `python3 -m refactor.tool match a+ a`, for example
  - This is a demo without assertions
- `./run.sh nfa-suite`
  - This is from the BurntSushi test suite, an unrelated "Dragon Book"
    implementation
  - the only failures are due to bad regex syntax, which is OK

## Backtracking Bug

Why is `a?a?a?aaa` is blowing up?

- Is the existing canonicalization OK, or do we need a new approach?
- It's based on tuples.  Write some unit tests

Commands:

- `./backtrack.sh compare-synthetic-rsc '' 20`
  - run one instance of this problem
- `./backtrack.sh compare-synthetic-rsc-all   # a?a? ... aaa ...`
  - run 3 instances with different N
- `./run.sh fgrep-problem-blowup  # aaa|bbb|ccc|...`
  - Runs unit tests showing the blowup

### Output

```
~/git/oilshell/epsilon (master)$ ./backtrack.sh compare-synthetic-rsc-all

=== synthetic-rsc, n = 15

   IMPL = epsilon   pat = a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?aaaaaaaaaaaaaaa

text aaaaaaaaaaaaaaa
        0.00067 Parsed
        0.19026 DFA
aaaaaaaaaaaaaaa
        0.19026 Matched

real    0m0.227s
user    0m0.218s
sys     0m0.008s

=== synthetic-rsc, n = 20

   IMPL = epsilon   pat = a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?aaaaaaaaaaaaaaaaaaaa

text aaaaaaaaaaaaaaaaaaaa
        0.00108 Parsed
        0.68500 DFA
aaaaaaaaaaaaaaaaaaaa
        0.68500 Matched

real    0m0.711s
user    0m0.711s
sys     0m0.000s

=== synthetic-rsc, n = 25

   IMPL = epsilon   pat = a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?aaaaaaaaaaaaaaaaaaaaaaaaa

text aaaaaaaaaaaaaaaaaaaaaaaaa
        0.00153 Parsed
        2.08398 DFA
aaaaaaaaaaaaaaaaaaaaaaaaa
        2.08398 Matched

real    0m2.110s
user    0m2.102s
sys     0m0.008s
```

## TODO

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
