# Serving `half_plus_two` model

In this example, we show how to serve a basic example model (`half_plus_two`) with
TensorFlow Serving using the prepared Docker image `tensorflow/serving`.

## Running a `tensorflow/serving` container

This image runs the command `tensorflow_model_server` which deploys a *ModelServer*
object implementing the default TensorFlow Serving logic for a specific model.

The configuration for this example is specified in the file
`tfserving_config.json`:

```
{
  "docker_image": "tensorflow/serving",
  "docker": [
    "--name half_plus_two",
    "-p 8500:8500",
    "-p 8501:8501",
    "-v $PWD/../models/half_plus_two_cpu:/models/half_plus_two",
    "-td"
  ],
  "tensorflow_model_server": [
    "--model_name=half_plus_two",
    "--model_base_path=/models/half_plus_two"
  ]
}
```

As you can see, the configuration file sets a list of options for the Docker command,
the Docker image to be used and additional parameters for the `tensorflow_model_server`
command.

- **Docker image**. The default `tensorflow/serving` image is used.
- **Docker options**. It is necessary to expose the ports 8500 and 8501 for communication
  with the serving via gRPC and REST API, respectively. It is also mandatory to bind a
  directory where the model is stored in the host.
- **TF Serving options**. It is necessary to set the model name and its base path, where
  the model is *stored* in the container.

Next, we pass this configuration file to the script `run_tfserving.py` which generates
a temporary script that runs a 'docker run' command.

```
bash ../utils/scripts/run_tfserving.sh tfserving_config.json
```

The temporaryly generated script would be similar to:

```
docker run --name half_plus_two \
           -p 8500:8500 \
           -p 8501:8501 \
           -v $PWD/../../models/half_plus_two_cpu:/models/half_plus_two \
           -itd \
           tensorflow/serving \
           --model_name=half_plus_two \
           --model_base_path=/models/half_plus_two
```

This way a container with a `tensorflow/serving` image is deployed in which the
`tensorflow_model_server` command is run to deploy the serving with the given options.

> The `run_tfserving.sh` script makes use of Python script `generate_docker_run.sh`,
  which parses the JSON config file and generates the `docker run` script file.

## Querying the model

Once the serving is deployed, you can check that it is working by querying it with a
`predict` action using the serving REST API and `curl`:

```
curl -d '{"instances" : [1.0, 2.0, 3.0, 4.0, 5.0]}' \
     -X POST http://localhost:8501/v1/models/half_plus_two:predict
```

This is implemented in `query.sh`:

```
bash query.sh
```

The response should be:

```
{
    "predictions": [2.5, 3.0, 3.5, 4.0, 4.5]
}
```
