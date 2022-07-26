pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh python \
    utils/rest_predict.py \
        -o 04_rest_predict_api/classify_result.json \
        04_rest_predict_api/classify.json;
popd;
