#!/usr/bin/env bash

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

if [ $# -eq 0 ]; then
  echo "ERROR: introduce a JSON with deployment configuration";
fi

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );
CONFIGDIR=$( cd -- "$( dirname -- "$1" )" &> /dev/null && pwd );
CONFIGPATH=$CONFIGDIR/$( basename -- "$1");

cp $CONFIGPATH $SCRIPTDIR/../../tmp_config.json;

pushd "$SCRIPTDIR"/../..;
  if [ $# -eq 1 ]; then
    ./run_in_docker.sh \
      python ./python/tfserving/grpc/query_grpc.py \
        -p \
        tmp_config.json;
  else
    ./run_in_docker.sh \
      python ./python/tfserving/grpc/query_grpc.py \
        "$2" "$3" \
        tmp_config.json;

    mv "$3" "$CONFIGDIR"/;
  fi;

  rm tmp_config.json
popd;