#!/usr/bin/env bash

# Usage: 'test <command> ...' to test a specific implementation, or
# 'test <name>' as a shortcut to test a specific implementation or all
# of them. The name can be 'all', 'original', 'dumb-translation',
# 'safe-translation', 'idiomatic-translation' or 'rust-regex'.

# Sanitize is off by default. When enabled, asan and ubsan for C programs is
# used. For Rust programs, Miri is used (but only when there is 'unsafe' in the
# program.)
: "${SANITIZE:=}"

# When enabled, show passing tests.
: "${VERBOSE:=}"

# When enabled, tests are skipped. Useful for just building a program.
: "${SKIPTEST:=}"

# cd to the directory containing this script.
cd "$(dirname "$0")"

# The format is one test per line. Each test has a pattern, haystack
# and expected result delimited by /. The expected result can be
# 'match', 'nomatch' or 'badsyntax'. Escaping / is not possible to keep
# the format and harness simple.
#
# Blank lines and lines starting with a # are ignored.
tests="
a//nomatch
a/a/match
a/ab/nomatch
a/ba/nomatch

a?//match
a?/a/match
a?/aa/nomatch

a*//match
a*/a/match
a*/aaaaa/match
a*/aaaaab/nomatch

# Oils PATCH: check double repetition
a**/aaaaa/match
a**/aaaaab/nomatch

a+//nomatch
a+/a/match
a+/aaaaa/match
a+/aaaaab/nomatch

abc//nomatch
abc/abc/match
abc/abcz/nomatch
abc/babc/nomatch

(abc)?//match
(abc)?/abc/match
(abc)?/aabc/nomatch

(abc)*//match
(abc)*/abc/match
(abc)*/abcabcabc/match
(abc)*/abcabcabca/nomatch
(abc)*/abcabcabcab/nomatch

(abc)+//nomatch
(abc)+/abc/match
(abc)+/abcabcabc/match
(abc)+/abcabcabca/nomatch
(abc)+/abcabcabcab/nomatch

a|b/a/match
a|b/b/match
a|b|c|d|e/d/match
abc|def/def/match
abc|def/abf/nomatch
sam|samwise/sam/match
sam|samwise/samwise/match
samwise|sam/sam/match
samwise|sam/samwise/match

(foo|bar|quux)+/quuxbarbarfoo/match
(foo|bar|quux)+(A|Z)qqq/quuxbarbarfooAqqq/match
(foo|bar|quux)+(A|Z)qqq/quuxbarbarfooZqqq/match

# The empty regex is not valid! The
# original program fails this test and
# actually seems to have UB.
//badsyntax

# Test that empty alternates are not allowed.
a||b/a/badsyntax
(a||b)/a/badsyntax
(a|)/a/badsyntax
# This triggers a bug in the original implementation as a result of
# the trailing |.
a|/a/badsyntax

# The original doesn't reject . which is a meta
# character in the postfix syntax. Results in UB.
a.b/a.b/badsyntax

# Other invalid patterns.
()//badsyntax
?//badsyntax
*//badsyntax
+//badsyntax
|//badsyntax
(a//badsyntax
a)//badsyntax
"

case "$1" in
  all)
    echo "=== original ==="
    ./test original
    echo "=== dumb-translation(rust) ==="
    ./test dumb-translation
    echo "=== safe-translation(rust) ==="
    ./test safe-translation
    echo "=== idiomatic-translation(rust) ==="
    ./test idiomatic-translation
    echo "=== regex crate ==="
    ./test rust-regex
    exit 0
    ;;
  original)
    ./original/build
    exec ./test ./original/nfa
    ;;
  dumb-translation)
    if [ -n "$SANITIZE" ]; then
      # We run it under Miri to check for UB. We also ignore leaks because
      # we specifically don't bother freeing memory, which mimics the
      # behavior of the original C implementation.
      MIRIFLAGS="-Zmiri-ignore-leaks" exec ./test \
        cargo miri run -q --manifest-path dumb-translation/Cargo.toml
    else
      cargo build -q --release --manifest-path dumb-translation/Cargo.toml
      exec ./test ./dumb-translation/target/release/nfa
    fi
    ;;
  safe-translation)
    cargo build -q --release --manifest-path safe-translation/Cargo.toml
    # We don't bother with miri here since we explicitly do not use unsafe. We
    # could use miri to detect the memory leaks in this program (as a result
    # of Rc cycles), but since the original program doesn't care about freeing
    # memory, we don't care here either.
    exec ./test ./safe-translation/target/release/nfa
    ;;
  idiomatic-translation)
    # The idiomatic translation uses no 'unsafe' and has no leaks.
    cargo build -q --release --manifest-path idiomatic-translation/Cargo.toml
    exec ./test ./idiomatic-translation/target/release/nfa
    ;;
  rust-regex)
    if [ -n "$SANITIZE" ]; then
      # The regex crate does have some uses of 'unsafe', so run Miri for good
      # measure.
      exec ./test cargo miri run -q --manifest-path rust-regex/Cargo.toml
    else
      cargo build -q --release --manifest-path rust-regex/Cargo.toml
      exec ./test ./rust-regex/target/release/nfa
    fi
    ;;
  "")
    echo "Usage: $(basename "$0") <command | alias>" >&2
    exit 1
    ;;
esac

if [ -n "$SKIPTEST" ]; then
  exit 0
fi
exitcode=0
while IFS=/ read -r pattern haystack result; do
  failed=
  case "$result" in
    match)
      if ! $* "$pattern" "$haystack" 2>&1 | grep -q -F -x -e "$haystack"; then
        failed=yes
      fi
      ;;
    nomatch)
      if $* "$pattern" "$haystack" 2>&1 | grep -q -F -x -e "$haystack"; then
        failed=yes
      fi
      ;;
    badsyntax)
      if ! $* "$pattern" "$haystack" 2>&1 | grep -q 'bad regexp'; then
        failed=yes
      fi
      ;;
  esac
  if [ -n "$failed" ]; then
    exitcode=1
    printf "%s/%s/%s ... FAILED\n" "$pattern" "$haystack" "$result"
  elif [ -n "$VERBOSE" ]; then
    printf "%s/%s/%s ... PASSED\n" "$pattern" "$haystack" "$result"
  fi
done < <(echo "$tests" | grep . | grep -v ^#)
exit $exitcode
