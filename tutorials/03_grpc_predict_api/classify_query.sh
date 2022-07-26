pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh python utils/grpc_predict.py 03_grpc_predict_api/classify.json -o 03_grpc_predict_api/result_classify.json;
popd;
