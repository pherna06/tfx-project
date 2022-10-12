#!/bin/bash

set -e

function usage() {
  echo "This script takes a JSON config file to deploy a TensorFlow Serving Docker container."
  echo "This config file must have:"
  echo "· 'docker_image': one of the available TensorFlow Serving images"
  echo "· 'docker': a list of Docker run command options"
  echo "· 'tensorflow_model_server': a list of options for the serving internal program"
  echo ""
  echo "Usage:"
  echo "  run_tfserving.sh [-o <docker-sh-file>] <docker-config-json>"
  echo ""
  echo "Options:"
  echo "  -o    Name for the generated script file. By default '.docker_run.sh' is used."
  return 1
}

(( $# < 1 )) && usage

DOCKERSCRIPT_NAME=".docker_run.sh"
while [[ $# > 1 ]]; do
  case "$1" in
    -o)
      DOCKERSCRIPT_NAME="$2"; shift 2;;
    *)
      break;;
  esac
done


if [[ $# < 1 ]]; then
  echo "No JSON config file given"
  return 1
fi

RUNNINGSCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );
CONFIGJSON_DIR=$( cd -- "$( dirname -- "$1" )" &> /dev/null && pwd );
CURRENT_DIR=$(pwd)

CONFIGJSON_PATH="$CURRENT_DIR"/"$1"
DOCKERSCRIPT_PATH="$CONFIGJSON_DIR"/"$DOCKERSCRIPT_NAME"


python "$RUNNINGSCRIPT_DIR"/../python/scripts/generate_docker_run.py \
  "$CONFIGJSON_PATH" \
  -o "$DOCKERSCRIPT_PATH"

. "$DOCKERSCRIPT_PATH"
rm "$DOCKERSCRIPT_PATH"
