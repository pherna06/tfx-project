pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd ..;
./utils/run_in_docker.sh python utils/tfserving.py 01_half_plus_two/half_plus_two.json;
chmod a+rwx docker.sh;
mv docker.sh 01_half_plus_two/;
popd;
./docker.sh;
rm docker.sh;
