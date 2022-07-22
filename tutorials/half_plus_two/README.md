# Serving `half_plus_two` model

In this example, we show how to serve a basic example model (`half_plus_two`) with
TensorFlow Serving using the prepared Docker image `tensorflow/serving`.

## Running a `tensorflow/serving` container

This image runs the command `tensorflow_model_server` which deploys a *ModelServer*
object implementing the default TensorFlow Serving logic for a specific model.

The configuration for this example is specified in the file
`half\_plus\_two.json`:

```
{
    "docker" : [
        "--name half_plus_two",
        "-p 8500:8500",
        "-p 8501:8501",
        "-v $PWD/../../models/half_plus_two_cpu:/models/half_plus_two",
        "-itd"
    ],

    "docker_image" : "tensorflow/serving",

    "tensorflow_model_server" : {
        "--model_name" : "half_plus_two",
        "--model_base_path" : "/models/half_plus_two"
    }
}
```

As you can see, the configuration file sets a list of options for the Docker command,
the Docker image to be used and additional parameters for the `tensorflow_model_server`
command.

- **Docker options**. It is necessary to expose the ports 8500 and 8501 for communication
  with the serving via gRPC and REST API, respectively. It is also mandatory to bind a
  directory where the model is stored in the host.
- **Docker image**. The default `tensorflow/serving` image is used.
- **TF Serving options**. It is necessary to set the model name and its base path, where
  the model is *stored* in the container.

Next, we pass this configuration file to the script `tfserving.py` which generates a
Docker `run` command given a configuration file like the previous one. In particular,
with this configuration, the command would be:

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

This command is written in a `docker.sh` script which we can use to deploy the container.

Script `deploy.sh` calls `tfserving.py` with `half_plus_two.json` as configuration file
and executes the generated `deploy.sh` script to run the serving as a container.

## Querying the model

Once the serving is deployed, you can check that it is working by querying it with a
`predict` action using the serving REST API and `curl`. Just use script `query.sh`:

```
curl -d '{"instances" : [1.0, 2.0, 3.0, 4.0, 5.0]}' \
     -X POST http://localhost:8501/v1/models/half_plus_two:predict
```

The response should be:

```
{
    "predictions": [2.5, 3.0, 3.5, 4.0, 4.5]
}
```
