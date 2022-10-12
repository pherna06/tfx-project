# TensorFlow Serving gRPC _Prediction_ API

Using gRPC (Google's framework implementing _remote procedure calls_), we can query
the models in our servings with different operations, which allow us to obtain
information about models and make inferences over them.

## Available gRPC APIs

First of all, it is important to notice that TensorFlow Serving defines 2 "gRPC APIs".
The one presented in this tutorial, which we will refer to as  _Prediction API_, comes
from the _protobuf_ implementation defined in
[`prediction_service.proto`](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/apis/prediction_service.proto).
In this file, we can observe the different types of queries that we can use:

```
service PredictionService {
  // Classify.
  rpc Classify(ClassificationRequest) returns (ClassificationResponse);

  // Regress.
  rpc Regress(RegressionRequest) returns (RegressionResponse);

  // Predict -- provides access to loaded TensorFlow model.
  rpc Predict(PredictRequest) returns (PredictResponse);

  // MultiInference API for multi-headed models.
  rpc MultiInference(MultiInferenceRequest) returns (MultiInferenceResponse);

  // GetModelMetadata - provides access to metadata for loaded models.
  rpc GetModelMetadata(GetModelMetadataRequest)
      returns (GetModelMetadataResponse);
}
```

The defined RPCs are oriented towards doing inferences over the model, and obtaining
information about the different inference operations available on a model.

On the other hand, the other "gRPC API" (_Model API_), which will be analyzed in another
tutorial, takes care of models loading and unloading within the serving.

## Example serving for gRPC querying

In this tutorial, we deploy a serving with 2 models: the basic _half\_plus\_two_ model and
a simple _MNIST_ model, obtained from TensorFlow Serving 
[guides](https://www.tensorflow.org/tfx/serving/serving_advanced#train_and_export_tensorflow_model).
In the first tutorial, we used the flags of `tensorflow_model_server` to specify the model
we wanted to serve(its name and path). However, we can deploy a serving that holds more than
one model, as long as the models' files are stored inside the serving Docker container. To do
that, we can use queries from _gRPC Model API_ to update the available models in the server or
we can pass a model configuration file to `tensorflow_model_server` using the flag
`--model_config_file`.

### `ModelServerConfig` message

This configuration file must be a _text-format protobuf_ file with the structure of a
[`ModelServerConfig`](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/config/model_server_config.proto)
message:

```
message ModelConfig {
  // Name of the model.
  string name = 1;

  // Base path to the model, excluding the version directory.
  string base_path = 2;

  // Type of model.
  ModelType model_type = 3 [deprecated = true];

  // Type of model (e.g. "tensorflow").
  string model_platform = 4;

  reserved 5, 9;

  // Version policy for the model indicating which version(s) of the model to
  // load and make available for serving simultaneously.
  // The default option is to serve only the latest version of the model.
  FileSystemStoragePathSourceConfig.ServableVersionPolicy model_version_policy = 7;

  // String labels to associate with versions of the model, allowing inference
  // queries to refer to versions by label instead of number. Multiple labels
  // can map to the same version, but not vice-versa.
  map<string, int64> version_labels = 8;

  // Configures logging requests and responses, to the model.
  LoggingConfig logging_config = 6;
}

// Static list of models to be loaded for serving.
message ModelConfigList {
  repeated ModelConfig config = 1;
}

// ModelServer config.
message ModelServerConfig {
  oneof config {
    ModelConfigList model_config_list = 1;
    google.protobuf.Any custom_model_config = 2;
  }
}
```

This message represents a list of the different models which will be loaded in the serving.
Each model has its own configuration: name, path to model, platform, version policy, version
labels and logging configuration. Besides, there is another option to use a custom model server
configuration, in case we wanted to extend TensorFlow serving to deal with our custom models.

### Obtaining a `ModelServerConfig` text-format file

To generate our `ModelServerConfig` file, we use the protobuf module `google.protobuf.text_format`.
This way, we just need to generate the message object with Python and use this utility to
export the message into a valid text-format file.

There also exists a protobuf _json-format_, which we can generate in a similar way using
module `google.protobuf.json_format`.

Finally, we can generate our model configuration file using terminal input with script 
`proto_tfserving.sh` which runs the command interface of the Python script `generate_proto.py`
inside a Docker container with a `tensorflow/serving` image (see `run_in_docker.sh` script).

While on this directory use:

```
bash ../utils/scripts/proto_tfserving.sh \
  gen -o model_server_config.txt         \
      -f text                            \
      ModelServerConfig
```

And we generate the message like this:

```
== Running with Docker...
> Generating 'ModelServerConfig' message...
> Add 'config' (oneof) field? (Yes: any | No 'n'):
> Available fields:
>   1.model_config_list (ModelConfigList)
>   2.[UNSUPPORTED] custom_model_config (google.protobuf.Any)
> Choose a field: 1
>> Generating 'ModelConfigList' message...
>> Add 'config' (repeated ModelConfig) field? (Yes: any | No 'n'):
>>   Add element to 'config'? (Yes: any | No 'n'):
>>> Generating 'ModelConfig' message...
>>> Add 'name' (string) field? (Yes: any | No 'n'):
>>>   Input 'name': half_plus_two
>>> Add 'base_path' (string) field? (Yes: any | No 'n'):
>>>   Input 'base_path': /models/half_plus_two
>>> Add 'model_platform' (string) field? (Yes: any | No 'n'):
>>>   Input 'model_platform' (e.g. 'tensorflow'): tensorflow
>>> Add 'model_version_policy' (ServableVersionPolicy) field? (Yes: any | No 'n'): n
>>> Add 'version_labels' (map<string, int64>) field? (Yes: any | No 'n'): n
>>> Add 'logging_config' (LoggingConfig) field? (Yes: any | No 'n'): n
>>> No more fields left in 'ModelConfig' message.
>>   Add element to 'config'? (Yes: any | No 'n'):
>>> Generating 'ModelConfig' message...
>>> Add 'name' (string) field? (Yes: any | No 'n'):
>>>   Input 'name': mnist
>>> Add 'base_path' (string) field? (Yes: any | No 'n'):
>>>   Input 'base_path': /models/mnist
>>> Add 'model_platform' (string) field? (Yes: any | No 'n'):
>>>   Input 'model_platform' (e.g. 'tensorflow'): tensorflow
>>> Add 'model_version_policy' (ServableVersionPolicy) field? (Yes: any | No 'n'): n
>>> Add 'version_labels' (map<string, int64>) field? (Yes: any | No 'n'): n
>>> Add 'logging_config' (LoggingConfig) field? (Yes: any | No 'n'): n
>>> No more fields left in 'ModelConfig' message.
>>   Add element to 'config'? (Yes: any | No 'n'): n
>> No more fields left in 'ModelConfigList' message.
> No more fields left in 'ModelServerConfig' message.
> text-format chosen.
Saving text-format protobuf in /home/pherna06/repos/pherna06/tfx-project/tutorials/03_grpc_prediction_api/test.txt
```

And obtain `model_server_config.txt`:

```
model_config_list {
  config {
    name: "half_plus_two"
    base_path: "/models/half_plus_two"
    model_platform: "tensorflow"
  }
  config {
    name: "mnist"
    base_path: "/models/mnist"
    model_platform: "tensorflow"
  }
}
```

### (OPTIONAL) More on `proto_tfserving.sh` script

We have generated the `model_server_config.txt` by typing the message fields on
on the terminal. However, the script provides an option to automatically load a
message fields from an input JSON file. For our previously generated file, this
input JSON file, `model_server_config.input.json` would look like this:

```
{
  "config": {
    "model_config_list": {
      "config": [
        {
          "name": "half_plus_two",
          "base_path": "/models/half_plus_two",
          "model_platform": "tensorflow"
        },
        {
          "name": "mnist",
          "base_path": "/models/mnist",
          "model_platform": "tensorflow"
        }
      ]
    }
  }
}
```

We add the input option to the script, and, in this case, we try the json-format
option (take into account, though, that `tensorflow_model_server` must receive the
file in text-format).

```
bash ../utils/scripts/proto_tfserving.sh \
  gen -i model_server_config.input.json  \
      -o model_server_config.json        \
      -f json                            \
      ModelServerConfig
```

The specified fields are filled automatically. but we are given the option to fill
in the rest of empty fields:

```
== Running with Docker...
> Generating 'ModelServerConfig' message...
> Setting 'model_config_list' from args...
>> Generating 'ModelConfigList' message...
>> Setting 'config' from args...
>>> Generating 'ModelConfig' message...
>>> Setting 'name' from args: half_plus_two
>>> Setting 'base_path' from args: /models/half_plus_two
>>> Setting 'model_platform' from args: tensorflow
>>> Add 'model_version_policy' (ServableVersionPolicy) field? (Yes: any | No 'n'): n
>>> Add 'version_labels' (map<string, int64>) field? (Yes: any | No 'n'): n
>>> Add 'logging_config' (LoggingConfig) field? (Yes: any | No 'n'): n
>>> No more fields left in 'ModelConfig' message.
>>> Generating 'ModelConfig' message...
>>> Setting 'name' from args: mnist
>>> Setting 'base_path' from args: /models/mnist
>>> Setting 'model_platform' from args: tensorflow
>>> Add 'model_version_policy' (ServableVersionPolicy) field? (Yes: any | No 'n'): n
>>> Add 'version_labels' (map<string, int64>) field? (Yes: any | No 'n'): n
>>> Add 'logging_config' (LoggingConfig) field? (Yes: any | No 'n'): n
>>> No more fields left in 'ModelConfig' message.
>> No more fields left in 'ModelConfigList' message.
> No more fields left in 'ModelServerConfig' message.
> json-format chosen.
Add customized pairs to JSON? (Yes: any | No 'n'):
Set key string for message: model_server_config
Add another key-value pair? (Yes: any | No 'n'): n
Saving json-format protobuf in /home/pherna06/repos/pherna06/tfx-project/tutorials/03_grpc_prediction_api/model_server_config.json
```

You should note that a final option is given to encapsulate the json-format protobuf
inside the output JSON file. In this case, we encapsulate it within the `model_server_config`
key. Besides, more key-values can be added to this JSON file (this option was implemented to
be used in a previous implementation of the GRPC query script, though it is not useful now).

Be aware too that the json-format message is not equal to our JSON input file:

```
"modelConfigList": {
  "config": [
    {
      "name": "half_plus_two",
      "basePath": "/models/half_plus_two",
      "modelPlatform": "tensorflow"
    },
    {
      "name": "mnist",
      "basePath": "/models/mnist",
      "modelPlatform": "tensorflow"
    }
  ]
}
```

Underscores are replaced by camelcase convention and, more importantly, in our input file
we need to specify the name of protobuf `oneof` variables (in this case, the `config`
prior to `modelConfigList`). In conclusion, a JSON input file should not be used as a
json-format protobuf file.

Finally, we have been using the `gen` subcommand to generate these protobuf files. But
there is another subcommand, `info`, which allows us to check the types of messages
(i.e. `ModelServerConfig`) and formats (i.e. `text`) available to generate. We can
both list them and search for specific types.

- An example listing formats:

```
bash ../utils/scripts/proto_tfserving.sh \
  info formats

Output:
== Running with Docker...
Available file formats:
· text
· json
```

- An example searching message types:

```
bash ../utils/scripts/proto_tfserving.sh \
  info messages                          \
       -s ModelServerConfig              \
          ModelSpec                      \
          UnknownMessage

Output:
== Running with Docker...
· ModelServerConfig (AVAILABLE)
· ModelSpec (AVAILABLE)
· UnknownMessage (UNKNOWN)
```

### Deploying the serving

Finally, we specify the configuration for deployment with Docker in `tfserving_config.json`,
exposing port 8500 for gRPC use as well as sharing our `models` directory with the
container:

```
{
  "docker_image": "tensorflow/serving",
  "docker": [
    "--name grpc_prediction_api",
    "-p 8500:8500",
    "-v $PWD/../models:/models",
    "-v $PWD/model_server_config.txt:/models/model_server_config.txt",
    "-td"
  ],
  "tensorflow_model_server": [
    "--model_config_file=/models/model_server_config.txt"
  ]
}
```

We deploy this container with `run_tfserving.sh` script:

```
bash ../utils/scripts/run_tfserving.sh tfserving_config.json
```

## gRPC Prediction API Operations

- [GetModelMetadata](http://github.com/pherna06/tfx-project/tree/master/tutorials/03_grpc_prediction_api/get_model_metadata)
- [Predict](http://github.com/pherna06/tfx-project/tree/master/tutorials/03_grpc_prediction_api/predict)
- [Classify](http://github.com/pherna06/tfx-project/tree/master/tutorials/03_grpc_prediction_api/classify)
- [Regress](http://github.com/pherna06/tfx-project/tree/master/tutorials/03_grpc_prediction_api/regress)
- [MultiInference](http://github.com/pherna06/tfx-project/tree/master/tutorials/03_grpc_prediction_api/multi_inference)