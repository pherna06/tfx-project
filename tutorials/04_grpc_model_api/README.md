# TensorFlow Serving gRPC _Model_ API

Using gRPC, we can query a serving:

- To obtain information about the available models and versions.
- To remove existing models or existing versions of a model.
- To add new models as well as new versiosn of an already existant model.
- The rename the labels (strings) that refer to different model versions.

To do all that, we use the gRPC _Model API_, derived from the _protobuf_
implementation defined in
[`model_service.proto`](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/apis/model_service.proto).
In this file, we can observe the different types of queries that we can use:

```
service ModelService {
  // Gets status of model. ...
  rpc GetModelStatus(GetModelStatusRequest) returns (GetModelStatusResponse);

  // Reloads the set of served models. The new config supersedes the old one.
  rpc HandleReloadConfigRequest(ReloadConfigRequest)
      returns (ReloadConfigResponse);
}
```

As we can see, only 2 RPCs are listed:

- With _GetModelStatus_, the serving is queried to receive status information of
  a specific model (that is, the different versions available).
- With _HandleReloadConfigRequest_, the serving is given a _protobuf_ message with
  the new model configuration for the serving (that is, for each model: name, path,
  versions...). The new configuration supersedes the old one, so removing an
  existant model in the message will unload that model in the serving.

## Example serving for gRPC querying.

As with _Prediction API_ tutorial, we deploy a serving with the same 2 models:
_half\_plus\_two_ and _MNIST_ models. In this case, we modifcy the `ModelServerConfig`
message, so that a custom version policy for each model is used (instead of the default
one, which, for each model, only loads the most recent (numerically higher) version).
This way:

- For _half\_plus\_two_, we specify to deploy all available versions. The only existant
  version `1` will be loaded.
- For _MNIST_, we specify to deploy versions `1, 2, 3` (this way the other available
  version `4` is not loaded in the serving).

In addition, we assign labels to deployed versions:

- `early` label for version `1` from _MNIST_ model.
- `stable` label for version `2` from _MNIST_ model and version `1` from _half\_plus\_two_ model.
- `canary` label for version `3` from _MNIST_ model.

These _labels_ are strings through which we can refer to the different model versions,
instead of using the versions numeric values. This way, when querying model versions
with gRPC _Prediction API_, we can use the version label.

However, by default, the serving does not allow to assign labels to non-existant model versions.
So, at serving start-up (no models are loaded), we would not be able to assign the labels within
the `ModelServerConfig` initial configuration. To make things easier, though, we can use
flag `--allow_version_labels_for_unavailable_models` from `tensorflow_model_server` to
overcome this problem. Note that label assignment to unexistant versions would be allowed
during the whole serving lifetime and care must be taken: a query to a version label whose
assigned model version is not loaded would result in an error.

All in all, we generate our `ModelServerConfig` message with an input file
(`model_server_config.input.json`) like this:

```
bash ../utils/scripts/proto_tfserving.sh \
  gen -i model_server_config.input.json  \
      -o model_server_config.txt         \
      -f text                            \
      ModelServerConfig
```

Obtaining `model_server_config.txt` protobuf message:

```
model_config_list {
  config {
    name: "half_plus_two"
    base_path: "/models/half_plus_two"
    model_platform: "tensorflow"
    model_version_policy {
      all {
      }
    }
    version_labels {
      key: "stable"
      value: 1
    }
  }
  config {
    name: "mnist"
    base_path: "/models/mnist"
    model_platform: "tensorflow"
    model_version_policy {
      specific {
        versions: 1
        versions: 2
        versions: 3
      }
    }
    version_labels {
      key: "canary"
      value: 3
    }
    version_labels {
      key: "early"
      value: 1
    }
    version_labels {
      key: "stable"
      value: 2
    }
  }
}
```

Finally, we deploy our serving as usual:

```
bash ../utils/scripts/run_tfserving.sh tfserving_config.json
```

## gRPC Prediction API Operations

- [GetModelStatus](http://github.com/pherna06/tfx-project/tree/master/tutorials/04_grpc_model_api/get_model_status)
- [HandleReloadConfigRequest](http://github.com/pherna06/tfx-project/tree/master/tutorials/04_grpc_model_api/handle_reload_config_request)