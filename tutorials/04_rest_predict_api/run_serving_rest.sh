pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh python \
    utils/tfserving.py \
        04_rest_predict_api/serving_rest.json;
chmod a+rwx docker.sh;
mv docker.sh 04_rest_predict_api/;
popd;

./docker.sh;
rm docker.sh;