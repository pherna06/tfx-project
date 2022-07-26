pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh \
    python utils/grpc_predict.py \
        -o 03_grpc_predict_api/predict_result.json \
        03_grpc_predict_api/predict.json;
popd;
