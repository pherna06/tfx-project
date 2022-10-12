#!/usr/bin/env bash

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

if [ $# -ne 1 ]; then
  echo "ERROR: introduce a JSON with deployment configuration";
fi

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );
CONFIGDIR=$( cd -- "$( dirname -- "$1" )" &> /dev/null && pwd );
CONFIGPATH=$CONFIGDIR/$( basename -- "$1");

cp $CONFIGPATH $SCRIPTDIR/../tmp_config.json;

pushd $SCRIPTDIR/..;
  ./run_in_docker.sh \
    python ./python/tfserving/generate_docker_sh.py \
      tmp_config.json;
  rm tmp_config.json;

  chmod a+rwx docker.sh;
  mv docker.sh $CONFIGDIR/;
popd;

pushd $CONFIGDIR;
  ./docker.sh
  rm docker.sh
popd;