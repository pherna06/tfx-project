pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh python utils/tfserving.py 03_grpc_predict_api/half_plus_two.json;
chmod a+rwx docker.sh;
mv docker.sh 03_grpc_predict_api/;
popd;
./docker.sh;
rm docker.sh;
