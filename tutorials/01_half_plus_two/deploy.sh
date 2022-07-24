pushd ..;
./utils/run_in_docker.sh python utils/tfserving.py 01_half_plus_two/half_plus_two.json;
chmod a+rwx docker.sh;
./docker.sh;
rm docker.sh;
popd;
