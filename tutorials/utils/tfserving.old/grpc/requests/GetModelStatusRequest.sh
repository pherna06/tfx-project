#!/usr/bin/env bash

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


echo "> !! Output file name should start with 'script_output'"

pushd "$SCRIPTDIR";
  pushd ../../..;
    ./run_in_docker.sh \
      python ./python/tfserving/grpc/requests/generate_GetModelStatusRequest.py;

    mv script_output* "$SCRIPTDIR"/;
  popd;
popd;

mv $SCRIPTDIR/script_output* ./;