#!/usr/bin/env bash

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "> !! Output file name should start with 'script_output'";
echo "> Automatic message configuration:";
echo ">   model_spec.name = mnist";
echo ">   model_spec.signature_def = predict_images";
echo ">   inputs['x'] = RANDOM_INPUT";
echo ">   output_filter = ['y']";

if [ $# -eq 2 ]; then
  pushd "$SCRIPTDIR"/../../../..;
    ./run_in_docker.sh \
      python ./python/models/mnist/grpc/requests/generate_random_PredictRequest.py \
        --out "$1" \
        "$2";

    mv "$1" "$SCRIPTDIR"/;
  popd;

  mv "$SCRIPTDIR"/"$1" ./;
else
  echo "ERROR: 2 argument needed (output file name, size)"
fi
