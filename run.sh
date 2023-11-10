#!/usr/bin/env bash
#
# Usage:
#   ./run.sh <function name>

set -o nounset
set -o pipefail
set -o errexit

### Tools (copied from rsc-regexp repo)

make-venv() {
  local dir=_tmp/venv
  mkdir -p $dir
  python3 -m venv $dir
}

install() {
  . _tmp/venv/bin/activate
  pip3 install mypy yapf tox
}

check() {
  . _tmp/venv/bin/activate

  #mypy py/nfa.py
}

format() {
  . _tmp/venv/bin/activate

  #yapf -i py/nfa.py
}


### Epsilon

build() {
  ### from README.md

  python3 setup.py build
  python3 setup.py install --user
}

eps() {
  # Highly annoying that it's here
  ~/.local/bin/epsilon "$@"
}

demo() {
  mkdir -p _tmp

  local out=_tmp/manual.py
  eps -o $out examples/manual.epsilon
  echo

  chmod +x $out
  cat $out

  echo
  cat README.md | python3 $out
}

gen-png() {
  local name=${1:-manual}
  eps -t dot -o _tmp/$name.dot examples/$name.epsilon 
  dot -Tpng -o _tmp/$name.png _tmp/$name.dot
}

gen-all-png() {
  set -x
  gen-png manual

  gen-png a
  gen-png bug1

  gen-png string
  gen-png utf8
}

count() {
  # exclude unicode DB
  ls epsilon/*.py | grep -v ucd.py | xargs wc -l
}

orig-tests() {
  . _tmp/venv/bin/activate

  python3 -m tox
}

execute() {
  local name=${1:-string}
  cli -t execute examples/$name.epsilon
}

test-string() {
  echo -n '"hi\n there \\ "' | execute
  echo -n '"hi\n there \"' | execute
}

test-unicode() {
  echo -n 'aZbZd' | execute unicode

  # This works, it matches a single char
  local mu=$'\u03bc'
  local s="a${mu}b${mu}d" 
  echo s=$s
  echo -n "$s" | execute unicode

  # This results in a Python error, not a epsilon error
  local bad=$'\xFF'
  local s="a${bad}b${bad}d" 
  echo -n "$s" | execute unicode

  # Hm this means that Epsilon is using the OPPOSITE strategy of RE2 / re2c.
  #
  # It does not compile unicode into the DFA, and operate on BYTES.
  #
  # Rather it uses code points only, with the big IntegerSet abstraction.  Hm.
}

cli() {
  # Geez this is the way to run
  python3 -m epsilon.cli "$@"
}

tool() {
  python3 -m epsilon.tool "$@"
}

test-tool() {
  set -x
  tool 'a+' a
  tool 'a+' b

  tool 'a' a

  # Bad syntax
  tool ')' a
  return
  tool '+' a
}

test-with-nfa-suite() {
  #../../oilshell/rsc-regexp/test $0 tool
  #bash -x ../../oilshell/rsc-regexp/test $0 tool

  # from BurntSushi/rsc-regexp
  ./nfa-suite.sh $0 tool
}

#
# Compare with re2c
#

re2c-gen() {
  local name=$1
  shift
  # Rest are flags

  set -x
  re2c "$@" --emit-dot -o _tmp/$name-re2c.dot examples/$name.re2c.h
  dot -Tpng -o _tmp/$name-re2c.png _tmp/$name-re2c.dot

  echo 'done'
}

re2c-string() {
  re2c-gen string
}

re2c-utf8() {
  # With --utf8 flag, we get the bigger DFA with UTF-8 support!

  re2c-gen unicode --utf8
  re2c-gen utf8-one --utf8
}

"$@"
