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
  pip3 install mypy yapf
}

check() {
  . _tmp/venv/bin/activate

  mypy py/nfa.py
}

format() {
  . _tmp/venv/bin/activate

  yapf -i py/nfa.py
}


### Epsilon

build() {
  ### from README.md

  python3 setup.py build
  python3 setup.py install --user
}

demo() {
  # Highly annoying
  ~/.local/bin/epsilon -o examples/manual.py examples/manual.epsilon
  echo
  cat examples/manual.py
}

"$@"
