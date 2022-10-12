#!/bin/bash

set -e

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

function usage() {
  echo "This script runs 'generate_proto.py' interface to generate protobuf messages."
  echo "Use '-h' option to see interface usage."
  return 1
}

(( $# < 1 )) && usage

CURRENT_DIR=$(pwd)

RUN_OPTS=()
if [[ "$1" == "-h" ]]; then
  RUN_OPTS+=("-h"); shift 1;
elif [[ "$1" == "info" ]]; then
  RUN_OPTS+=("info"); shift 1;
  while [[ $# > 0 ]]; do
    case "$1" in
      -h)
        RUN_OPTS+=("-h"); shift 1;;
      -s)
        RUN_OPTS+=("-s"); shift 1;;
      *)
        RUN_OPTS+=("$1"); shift 1;;
    esac
  done
elif [[ "$1" == "gen" ]]; then
  RUN_OPTS+=("gen"); shift 1;
  while [[ $# > 0 ]]; do
    case "$1" in
      -h)
        RUN_OPTS+=("-h"); shift 1;;
      -f)
        RUN_OPTS+=("-f $2"); shift 2;;
      --format)
        RUN_OPTS+=("-f $2"); shift 2;;
      -i)
        INPUT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("-i $INPUT_PATH"); shift 2;;
      --input)
        INPUT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("-i $INPUT_PATH"); shift 2;;
      -o)
        OUTPUT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("-o $OUTPUT_PATH"); shift 2;;
      --output)
        OUTPUT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("-o $OUTPUT_PATH"); shift 2;;
      *)
        RUN_OPTS+=("$1"); shift 1;;
    esac
  done
fi

RUNNINGSCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );

pushd "$RUNNINGSCRIPT_DIR/.."
  bash run_in_docker.sh \
    -o "-v $CURRENT_DIR:$CURRENT_DIR"\
    python python/scripts/generate_proto.py \
      ${RUN_OPTS[@]}
popd