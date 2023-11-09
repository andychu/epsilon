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
  eps -t dot -o _tmp/manual.dot examples/manual.epsilon 
  dot -Tpng -o _tmp/manual.png _tmp/manual.dot
}

count() {
  # exclude unicode DB
  ls epsilon/*.py | grep -v ucd.py | xargs wc -l
}

orig-tests() {
  . _tmp/venv/bin/activate

  python3 -m tox
}

"$@"
