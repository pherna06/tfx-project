# Predict

This operation is used for performing inference of a model.
[`Predict SignatureDef`](https://www.tensorflow.org/tfx/serving/signature_defs#predict_signaturedef)
supports many input and output Tensors. For the example below, the signature
`my_prediction_signature` has a single logical input Tensor `images` that are mapped
to the actual Tensor in your graph `x:0`.

```
signature_def: {
  key  : "my_prediction_signature"
  value: {
    inputs: {
      key  : "images"
      value: {
        name: "x:0"
        dtype: ...
        tensor_shape: ...
      }
    }
    outputs: {
      key  : "scores"
      value: {
        name: "y:0"
        dtype: ...
        tensor_shape: ...
      }
    }
    method_name: "tensorflow/serving/predict"
  }
}
```

`Predict SignatureDefs` enable portability across models. This means that you can swap in
different `SavedModels`, possibly with a different underlying Tensor names (for example,
`z:0` instead of `x:0`), while your clients can stay online continuosly querying the old
and new versions of this model without client-side changes.

They also allow you to add optional additional Tensors to the outputs, that you can
explicitly query. Let's say that in addition to the output key below `scores`, you also
wanted to fetch a pooling layer for debugging or other purposes. In that case, you would
simply add an additional Tensor with a key like `pool` and appropiate value.

## Generating the request protobuf file for `half_plus_two` model.

To perform this operation we generate a text-format protobuf `PredictRequest` using the
the `proto_tfserving.sh` script.

In a `PredictRequest` protobuf, the field `inputs` takes key-value elements that store
the inputs of our inference request to the model. These inputs are of the type `TensorProto`,
a relatively complex protobuf message type. To avoid having to deal with this complexity,
we use the TensorFlow method
[`make_tensor_proto`](https://www.tensorflow.org/api_docs/python/tf/make_tensor_proto),
that takes a list as input to generate the Tensor structure.

Now, to query the `half_plus_two` model, we take a look to the response of the model to
the `GetModelMetadata` query:

```
...
signature_def {
  key: "serving_default"
  value {
    inputs {
      key: "x"
      value {
        name: "x:0"
        dtype: DT_FLOAT
        tensor_shape {
          dim {
            size: -1
          }
          dim {
            size: 1
          }
        }
      }
    }
    outputs {
      key: "y"
      value {
        name: "y:0"
        dtype: DT_FLOAT
        tensor_shape {
          dim {
            size: -1
          }
          dim {
            size: 1
          }
        }
      }
    }
    method_name: "tensorflow/serving/predict"
  }
...
```

As we can see, the only signature that uses a _Predict_ inference type is that with
the name `serving_default`. As inputs, it takes an only tensor named `x`, and as outputs,
it generates an only tensor named `y`. In particular, this models takes individual scalars
as input, so making an inference of, for example, 5 samples would require a list of 5
scalars, i.e.: `[1.0, 2.0, 3.0, 5.0, 7.0]`.

With this analysis, we call the script to generate the request:

```
bash ../../utils/scripts/proto_tfserving.sh        \
  gen -f text                                      \
      -o half_plus_two.serving_default.request.txt \
      PredictRequest
```

And fill in the needed message fields:

```
== Running with Docker...
> Generating 'PredictRequest' message...
> Add 'model_spec' (ModelSpec) field? (Yes: any | No 'n'):
>> Generating 'ModelSpec' message...
>> Add 'name' (string) field? (Yes: any | No 'n'):
>>   Input 'name': half_plus_two
>> Add 'version_choice' (oneof) field? (Yes: any | No 'n'): n
>> Add 'signature_name' (string) field? (Yes: any | No 'n'):
>>   Input 'signature_name': serving_default
>> No more fields left in 'ModelSpec' message.
> Add 'inputs' (map<string, TensorProto>) field? (Yes: any | No 'n'):
>   Add element to 'inputs'? (Yes: any | No 'n'):
>     Input element key (string): x
>     Input element value (as list): [1.0, 2.0, 3.0, 5.0, 7.0]
>   Add element to 'inputs'? (Yes: any | No 'n'): n
> Add 'output_filter' (repeated string) field? (Yes: any | No 'n'):
>   Add element to 'output_filter'? (Yes: any | No 'n'):
>     Input element (string): y
>   Add element to 'output_filter'? (Yes: any | No 'n'): n
> No more fields left in 'PredictRequest' message.
> text-format chosen.
Saving text-format protobuf in /home/pherna06/repos/pherna06/tfx-project/tutorials/03_grpc_prediction_api/predict/half_plus_two.serving_default.request.txt
```

...obtaining the `half_plus_two.serving_default.request.json` file:

```
model_spec {
  name: "half_plus_two"
  signature_name: "serving_default"
}
inputs {
  key: "x"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 5
      }
    }
    tensor_content: "\000\000\200?\000\000\000@\000\000@@\000\000\240@\000\000\340@"
  }
}
output_filter: "y"
```

> Note that the tensor content is byte-encoded.

## Generating the request protobuf file for `mnist` model.

In case of the `mnist` model (which resembles a more usual model than `half_plus_two`),
the samples used for model inferencing represent images. Indeed, each sample represents
a `B&W 28 x 28` image and is represented as an array with `28 x 28 = 784` elements in
the range `[0.0, 1.0]`.

> This information cannot be found in the response to the GetModelMetadata request.
  I have found it in code of the example
  [script](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/example/mnist_input_data.py)
  used for querying this same model.

As such, typing a 784 elements list to generate a model is not practical, so we include
a specific `PredictRequest` for `mnist` in our `proto_tfserving.sh` script, that asks for
the number of samples and generates them randomly.

Besides, the signature name for the only _Predict_ method in the model is called `predict_images`. Finally, we call the script:


```
bash ../../utils/scripts/proto_tfserving.sh \
  gen -f text                               \
      -o mnist.predict_images.request.txt   \
      mnist:predict_images:PredictRequest
```

And fill in the asked data:


```
== Running with Docker...
> Generating 'PredictRequest' message...
> Setting 'model_spec' from args...
>> Generating 'ModelSpec' message...
>> Setting 'name' from args: mnist
>> Add 'version_choice' (oneof) field? (Yes: any | No 'n'): n
>> Setting 'signature_name' from args: predict_images
>> No more fields left in 'ModelSpec' message.
> Add 'inputs' (map<string, TensorProto>) field? (Yes: any | No 'n'):
>   Randomly generating Tensor with key 'images' with sample size of 784.
>     Input number of samples (int): 5
> Add 'output_filter' (repeated string) field? (Yes: any | No 'n'):
>   Available outputs: ['scores']
>   Add element to 'output_filter'? (Yes: any | No 'n'):
>     Input element (string): scores
>   Add element to 'output_filter'? (Yes: any | No 'n'): n
> No more fields left in 'PredictRequest' message.
> text-format chosen.
Saving text-format protobuf in /home/pherna06/repos/pherna06/tfx-project/tutorials/03_grpc_prediction_api/predict/mnist.predict_images.request.txt
```

...obtaining the `mnist.predict_images.request.txt` protobuf file.

## Querying the serving with a `Predict` request.

We query the serving using `grpc_tfserving.sh`:

For `half_plus_two`:

```
bash ../../utils/scripts/grpc_tfserving.sh                 \
  query prediction                                         \
    Predict                                                \
    --in_text half_plus_two.serving_default.request.txt    \
    --out_json half_plus_two.serving_default.response.json \
    --out_text half_plus_two.serving_default.response.txt
```

For `mnist`:

```
bash ../../utils/scripts/grpc_tfserving.sh        \
  query prediction                                \
    Predict                                       \
    --in_text mnist.predict_images.request.txt    \
    --out_json mnist.predict_images.response.json \
    --out_text mnist.predict_images.response.txt
```

The output files resulting from these queries are saved in this directory.

- In the case of `half_plus_two` model, the response results of dividing by 2
and adding 2 to the given values.

- In the case of `mnist` model, the response represents, for each of the 5
  images, the probability value for that image belonging to each of the 10
  classes the model is made to detect.