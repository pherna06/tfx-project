#!/usr/bin/env bash

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "> Currently supported metadata fields: \"signature_def\""

if [ $# -eq 1 ]; then
  pushd "$SCRIPTDIR";
    pushd ../../..;
      ./run_in_docker.sh \
        python ./python/tfserving/grpc/requests/generate_GetModelMetadataRequest.py \
          --out "$1";

      mv "$1" "$SCRIPTDIR"/;
    popd;
  popd;

  mv "$SCRIPTDIR"/"$1" ./;
else
  echo "ERROR: 1 argument needed (output file name)"
fi