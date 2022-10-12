#!/bin/bash

set -e

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

function usage() {
  echo "This script runs 'query_grpc.py' interface to query a serving with GRPC requests."
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
      protobuf)
        RUN_OPTS+=("protobuf"); shift 1;;
      model)
        RUN_OPTS+=("model"); shift 1;;
      prediction)
        RUN_OPTS+=("prediction"); shift 1;;
      *)
        break;;
    esac
  done
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
elif [[ "$1" == "query" ]]; then
  RUN_OPTS+=("query"); shift 1;
  while [[ $# > 0 ]]; do
    case "$1" in
      -h)
        RUN_OPTS+=("-h"); shift 1;;
      model)
        RUN_OPTS+=("model"); shift 1;;
      prediction)
        RUN_OPTS+=("prediction"); shift 1;;
      *)
        break;;
    esac
  done
  while [[ $# > 0 ]]; do
    case "$1" in
      -h)
        RUN_OPTS+=("-h"); shift 1;;
      -s)
        RUN_OPTS+=("-s $2"); shift 2;;
      --in_json)
        INJSON_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("--in_json $INJSON_PATH"); shift 2;;
      --in_text)
        INTEXT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("--in_text $INTEXT_PATH"); shift 2;;
      -d)
        RUN_OPTS+=("-d"); shift 1;;
      --out_json)
        OUTJSON_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("--out_json $OUTJSON_PATH"); shift 2;;
      --out_text)
        OUTTEXT_PATH="$CURRENT_DIR/$2"
        RUN_OPTS+=("--out_text $OUTTEXT_PATH"); shift 2;;
      -p)
        RUN_OPTS+=("-p"); shift 1;;
      *)
        RUN_OPTS+=("$1"); shift 1;;
    esac
  done
fi

RUNNINGSCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );

pushd "$RUNNINGSCRIPT_DIR/.."
  bash run_in_docker.sh \
    -o "-v $CURRENT_DIR:$CURRENT_DIR"\
    python python/scripts/query_grpc.py \
      ${RUN_OPTS[@]}
popd