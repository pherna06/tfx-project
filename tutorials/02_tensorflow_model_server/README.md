# Flags for `tensorflow_model_server`

In the previous tutorial, we deployed a simple model with TensorFlow Serving using the
default configuration. However, `tensorflow_model_server` presents many configuration
options that we study in here.

File `default_config.json` contains all available options (and its default values) for
`tensorflow_model_server` command. We analize them one by one.

## gRPC API Configuration

### `--port`

> TCP port to listen on for gRPC/HTTP API. Disabled if port set to zero.

### `--grpc_socket_path`

> If non-empty, listen to a UNIX socket for gRPC API on the given path. Can be either
  relative or absolute path.

### `--grpc_channel_arguments`

> A comma separated list of arguments to be passed to the gRPC server.
  (e.g. `grpc.max_connection_age_ms=2000`)

### `--grpc_max_threads`

> Max gRPC server threads to handle gRPC messages.

## REST API Configuration

### `--rest_api_port`

> Port to listen on for HTTP/REST API. If set to zero HTTP/REST API will not be exported.
  This port must be different than the one specified in `--port`

### `--rest_api_num_threads`

> Number of threads for HTTP/REST API processing. If not set, will be auto set based on
  number of CPUs.

### `--rest_api_timeout_in_ms`

> Timeout for HTTP/REST API calls.

### `--rest_api_enable_cors_support`

> Enable CORS headers in response.

## Batching Configuration

Refer to TensorFlow Serving
[batching guide](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/batching/README.md)
for an in-depth discussion on batching.

Refer to the TensorFlow Serving
[section on parameters](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/batching/README.md#batch-scheduling-parameters-and-tuning)
to understand how to set the batching parameters.

### `--enable_batching`

> Enable batching.

### `--batching_parameters_file`

> If non-empty, read an ASCII BatchingParameters protobuf from the supplied file name and
  use the contained values instead of the defaults.

Example batching parameters file:

```
max_batch_size { value : 128 }
batch_timeout_micros { value: 0 }
max_enqueued_batches { value: 1000000 }
num_batch_threads { value: 8 }
```

## Model Server Configuration

### `--model_config_file`

> If non-empty, read an ASCII ModelServerConfig protobuf from the supplied name, and serve
  the models in that file. This config gile can be used to specify multiple models to serve
  and other advanced parameteres including non-default version policy.

### `--model_config_file_poll_wait_seconds`

> Interval in seconds between each poll of the filesystem for `model_config_file`. If unset
  or set to zero, poll will be done exactly once and not periodically. Setting this to
  negative is reserved for testing purposes only.

### `--model_name`

> Name of model (ignored if `--model_config_file` flag is set).

### `--model_base_path`

> Path to export (ignored if `--model_config_file` flag is set, otherwise required).

### `--allow_version_labels_for_unavailable_models`

> If true, allows assigning unused version labels to models that are not available yet.

### `--enable_model_warmup`

> Enables model warmup, which triggers lazy initializations (such as TensorFlow
  optimizations) at load time, to reduce first request latency.

Check
[SavedModel Warmup](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/g3doc/saved_model_warmup.md)
for more information on this topic.

### `--saved_model_tags`

> Comma-separated set of tags corresponding to the MetaGraphDef to load from SavedModel.

MetaGraphDefs should be tagged with their capabilites or use-cases. For example:
`train`, `serve`, `gpu`, `tpu`, etc. These tags enable loaders to access the MetaGraph
appropiate for a specific use-case or runtime environment.

### `--enable_signature_method_name_check`

> Enable `method_name` check for `SignatureDef`. Disable this if serving native TF2
  regression/classification models.

If set, method names for model signatures are checked to match with TensorFlow default
SignatureDefs (i.e. `tensorflow/serving/predict`).

See
[SignatureDefs in SavedModel for TensorFlow Serving](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/g3doc/signature_defs.md)
for more information on `SignatureDef`.

### Reloading Model Server Configuration

There are two ways to reload the Model Server configuration:

- By setting the `--model_config_file_poll_wait_seconds` flag to instruct the server to
  periodically check for a new config file at `--model_config_file` filepath.

- By issuing `HandleReloadConfigRequest` RPC calls to the server and supplying a new
  Model Server config programatically.

Please note that each time the server loads the new config file, it will act to realize
the contente of the new specified config and *only* the new specified config. This means
if model A was present in the first config file, which is replaced with a file that
contains only model B, the server will load model B and unload model A.

The Model Server configuration file provided must be a `ModelServerConfig` protobuf.

For all the most advanced use-cases, you will want to use the `ModelConfigList` option,
which is a list of `ModelConfig` protobufs. Here is a basic example:

```
model_config_list {
    config {
        name: 'my_first_model'
        base_path: '/tmp/my_first_model/'
        model_platform: 'tensorflow'
    }
    config {
        name: 'my_second_model'
        base_path: '/tmp/my_second_model/'
        model_platform: 'tensorflow'
    }
}
```

See
[ModelConfig](https://github.com/tensorflow/serving/tree/master/tensorflow_serving/config/model_server_config.proto)
for the whole protobuf structure.

In each `ModelConfig` you can specify a specific version of the model with the option
`ModelVersionPolicy`.

For example, to pin version 42 as the one to server:

```
model_config_list {
    ...
    config {
        ...
        model_version_policy {
            specific {
                versions: 42
            }
        }
    }
}
```

You can also serve multiple versions of the model simultaneously. For example, serve
versions 42 and 43:

```
model_config_list {
    ...
    config {
        ...
        model_version_policy {
            specific {
                versions: 42
                versions: 43
            }
        }
    }
}
```

Sometimes it is helpful to add a level of indirection to model versions. Instead of
letting all your clients know that they should be querying version 42, you can assign an
alias such as *stable* to whichever version is currently the one clients should query. If
you want to redirect a slice of traffic to a tentative canary model version, you can use
a second alis *canary*.

You can configure these model versions aliases, or labels, like so:

```
model_config_list {
    ...
    config {
        ...
        model_version_policy {
            specific {
                versions: 42
                versions: 43
            }
        }
        version_labels {
            key: 'stable'
            value: 42
        }
        version_labels {
            key: 'canary'
            value: 43
        }
    }
}
```

Please note that labels can only be assigned to model versions that are already loaded and
available for serving. Once a model version is available, one may reload the model config
on the fly to assign a label to it.

If you would like to assign a label to a version that is not yet loaded (for example, at
startup time) then you must set the `--allow_version_labels_for_unavailable_models` flag to
`true`, which allows new labels to be assigned to model versions that are not loaded yet.

Please note that this applies only to new version labels (i.e. ones not assigned to a
version currently). This is to ensure that during version swaps, the server does not
prematurely assign the label to the new version, thereby dropping all requests destined
for that label while the new version is loading.

In order to comply with this safety check, if re-assigning an already in-use version label,
you must assign it only to already-loaded versions. For example, if you would like to move
a label from pointing to version N to version N+1, you may first submit a config containing
version N and N+1, and then submit a config that contains version N+1, the label pointing
to N+1 and no version N.

## TensorFlow Lite Configuration

### `--prefer_tflite_model`

> EXPERIMENTAL; CAN BE REMOVED ANYTIME! Prefer TensorFlow Lite model from `model.tflite`
file in SavedModel directory, instead of the TensorFlow model from `saved_model.pb` file.
If no TensorFlow Lite model found, fallback to TensorFlow model.

### `--num_tflite_pools`

> EXPERIMENTAL; CAN BE REMOVED ANYTIME! Number of TFLite interpreters in an interpreter
pool of TfLiteSession. Typically there is one TfLiteSession for each TF Lite model that
is loaded. If not set, will be auto set based on number of CPUs.

### `--num_tflite_interpreters_per_pool`

> EXPERIMENTAL; CAN BE REMOVED ANYTIME! Number of TFLite interpreters in an interpreter
pool of TfLiteSession. Typically there is one TfLiteSession for each TF Lite model that
is loaded. If not set, will be 1.

## Model Load/Unload Configuration

### `--num_load_threads`

> The number of threads in the thread-pool used to load servables. If set as 0, we do not
  use a thread-pool, and servable loads are performed serially in the manager's main work
  loop, may cause the Serving request to be delayed. Default: 0.

### `--num_unload_threads`

> The number of threads in the thread-pool used to unload servables. If set as 0, we do not
  use a thread-pool, and servable loads are performed serially in the manager's main work
  loop, may casue the Serving request to be delayed. Default: 0.

### `--max_num_load_retries`

> Maximum number of times it retries loading a model after the first failure, before
  giving up. If set to 0, a load is attempted only once. Default: 5.

### `--load_retry_interval_micros`

> The interval, in microseconds, between each servable load retry. If set negative, it
  does not wait. Default: 1 minute.

## Serving Filesystem Configuration

### `--file_system_poll_wait_seconds`

> Interval in seconds between each poll of the filesystem for new model version. If set to
  0, poll will be exactly done once and not periodically. Setting this to negative value
  will disable polling entirely causing ModelServer to indefinitely wait for a new model
  at startup. Negativa values are reserved for testing purposes only.

### `--flush_filesystem_caches`

> If true (the default), filesystem caches will be flushed after the initial load of all
  servables, and after each subsequent individual servable reload (if the number of load
  threads is 1). This reduces memory consumption of the model server, at the potential
  cost of cache misses if model files are accessed after servables are loaded.

## TensorFlow Session Parallelism

Note that if `--tensorflow_session_parallelism` is used, then
`--tensorflow_intra_op_parallelism` and `--tensorflow_inter_op_parallelism` cannot be set.

### `--tensorflow_session_parallelism`

> Number of threads to use for running a Tensorflow session. Auto-configured by default.
  Note that this option is ignored if `--platform_config_file` is non-empty.

### `--tensorflow_intra_op_parallelism`

> Number of threads to use to parallelize the execution of an individual op.
  Auto-configured by default. Note that this option is ignored if `--platform_config_file`
  is non-empty.

### `--tensorflow_inter_op_parallelism`

> Controls the number of operators that can be executed simultaneously. Auto-configured by
  default. Note that this option is ignored if `--platform_config_file` is non-empty.

## Other Configurations

### `--ssl_config_file`

> If non-empty, read an ASCII SSLConfig protobuf from the supplied file name and set up a
  secure gRPC channel.

Example `SSLConfig` file:

```
server_key { value: '$KEY' }
server_cert { value: '$CERT' }
custom_ca { value: '$CA' }
client_verify { value: true }
```

### `--platform_config_file`

> If non-empty, read an ASCII PlatformConfigMap protobuf from the supplied file name, and
  use that platform config instead of the TensorFlow platform. If used, `--enable_batching`
  is ignored.

Example `PlatformConfigMap` file:

```
platform_configs {
    key: 'tensorflow'
    value {
        source_adapter_config {
            type_url: 'type.googleapis.com/tensorflow.serving.SavedModelBundleSourceAdapterConfig',
            value: '\xc2>\x04\x12\x028\x01'
        }
    }
}
```

The `value` field in `source_adapter_config` holds the serialized
`SavedModelBundleSourceAdapterConfig` that you want to use.

For more information see
[Issue 342](https://github.com/tensorflow/serving/issues/342).


### `--monitoring_config_file`

> If non-empty, read an ASCII MonitoringConfig protobuf from the supplied file name.

Example `MonitoringConfig` file:

```
prometheus_config {
    enable: true
    path: '/monitoring/prometheus/metrics'
}
```

For now, only Prometheus monitoring is allowed. Besides, to read metrics from the above
URL, you first need to enable the HTTP server by setting `--rest_api_port` flag. You can
then configure your Prometheus Server to pull metrics from Model Server by passing it the
values of `--rest_api_port` and `path`.

TensorFlow Serving collects all metrics that are captured by Serving as well as core
TensorFlow.

## Miscellaneous Flags

### `--per_process_gpu_memory_fraction`

> Fraction that each process occupies of the GPU memory space. The value is between 0.0 and
  1.0 (with 0.0 as the default). If 1.0, the server will allocate all the memory at
  startup. If 0.0, TensorFlow will automatically select a value.

### `--remove_unused_fields_from_bundle_metagraph`

> Remove unused fields from MetaGraphDef proto message to save memory.

### `--xla_cpu_compilation_enabled`

> EXPERIMENTAL; CAN BE REMOVED ANYTIME! Enable XLA:CPU JIT (default is disabled). With 
  XLA:CPU JIT disabled, models utilizaing this feature will return bad Status on first
  compilation request.

### `--enable_profiler`

> Enable profiler service.

For more information see
[TensorFlow Profiler](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras).

### `--version`

> Display version.

## TODO: config files and miscellaneous
