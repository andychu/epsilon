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
  gen-png string
}

count() {
  # exclude unicode DB
  ls epsilon/*.py | grep -v ucd.py | xargs wc -l
}

orig-tests() {
  . _tmp/venv/bin/activate

  python3 -m tox
}

#
# Compare with re2c
#

re2c-gen() {
  local name=${1:-string}

  set -x
  re2c --emit-dot -o _tmp/$name-re2c.dot examples/$name.re2c.h
  dot -Tpng -o _tmp/$name-re2c.png _tmp/$name-re2c.dot

  echo 'done'
}

"$@"
