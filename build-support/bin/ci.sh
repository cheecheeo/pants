#!/usr/bin/env bash

source build-support/set_archflags.sh

function banner() {
  echo
  echo "[== $@ ==]"
  echo
}

function die() {
  if (( $# > 0 )); then
    echo -e "\n$@"
  fi
  exit 1
}

function usage() {
  echo "Runs commons tests for local or hosted CI."
  echo
  echo "Usage: $0 (-h|-bsdjp)"
  echo " -h           print out this help message"
  echo " -b           skip bootstraping pants from local sources"
  echo " -s           skip self-distribution tests"
  echo " -d           if running jvm tests, don't use nailgun daemons"
  echo " -j           skip jvm tests"
  echo " -p           skip python tests"
  echo " -c           skip pants integration tests"
  if (( $# > 0 )); then
    die "$@"
  else
    exit 0
  fi
}

daemons="--ng-daemons"

while getopts "hbsdjpc" opt; do
  case ${opt} in
    h) usage ;;
    b) skip_bootstrap="true" ;;
    s) skip_distribution="true" ;;
    d) daemons="--no-ng-daemons" ;;
    j) skip_java="true" ;;
    p) skip_python="true" ;;
    c) skip_integration="true" ;;
    *) usage "Invalid option: -${OPTARG}" ;;
  esac
done

banner "CI BEGINS"

if [[ "${skip_bootstrap:-false}" == "false" ]]; then
  banner "Bootstrapping pants"
  (
    PANTS_VERBOSE=1 PEX_VERBOSE=1 PYTHON_VERBOSE=1 ./pants;
    ./pants.pex goal goals
  ) || die "Failed to bootstrap pants."
fi

./pants.pex goal goals || die "Failed to list goals."
./pants.pex goal list :: || die "Failed to list all targets."

# TODO(John sirois): Re-plumb build such that it grabs constraints from the built python_binary
# target(s).
INTERPRETER_CONSTRAINTS=(
  "CPython>=2.6,<3"
  "CPython>=3.3"
)
for constraint in ${INTERPRETER_CONSTRAINTS[@]}; do
  INTERPRETER_ARGS=(
    ${INTERPRETER_ARGS[@]}
    --interpreter="${constraint}"
  )
done

if [[ "${skip_distribution:-false}" == "false" ]]; then
  # TODO(John Sirois): Take this further and dogfood a bootstrap from the sdists generated by
  # setup_py
  banner "Running pants distribution tests"
  (
    ./pants.pex py --pex ${INTERPRETER_ARGS[@]} \
      src/python/pants:_pants_transitional_publishable_binary_ && \
    mv dist/_pants_transitional_publishable_binary_.pex dist/self.pex && \
    ./dist/self.pex build ${INTERPRETER_ARGS[@]} \
      src/python/pants:_pants_transitional_publishable_binary_ && \
    ./dist/self.pex setup_py --recursive src/python/pants:pants-packaged
  ) || die "Failed to create pants distributions."
fi

if [[ "${skip_java:-false}" == "false" ]]; then
  banner "Running jvm tests"
  (
    ./pants.pex goal test {src,tests}/{java,scala}:: $daemons
  ) || die "Jvm test failure."
fi

if [[ "${skip_python:-false}" == "false" ]]; then
  banner "Running python tests"
  (
    PANTS_PYTHON_TEST_FAILSOFT=1 ./pants.pex goal test tests/python/pants_test:all \
      ${INTERPRETER_ARGS[@]}
  ) || die "Python test failure"
fi

if [[ "${skip_integration:-false}" == "false" ]]; then
  banner "Running Pants Integration tests"
  (
    PANTS_PYTHON_TEST_FAILSOFT=1 ./pants.pex goal test tests/python/pants_test:integration \
      ${INTERPRETER_ARGS[@]}
  ) || die "Pants Integration test failure"
fi

banner "CI SUCCESS"
