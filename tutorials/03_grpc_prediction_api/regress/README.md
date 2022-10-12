# Regress

This operation is used for performing a regression inference of a model.
[`Regress SignatureDef`](https://www.tensorflow.org/tfx/serving/signature_defs#regression_signaturedef)
supports structured calls to TensorFlow Serving's Regression API. These
prescribe that there must be exactly one `inputs` Tensor, and one `outputs`
Tensor.

```
signature_def: {
  key  : "my_regression_signature"
  value: {
    inputs: {
      key  : "inputs"
      value: {
        name: "x_input_examples_tensor_0"
        dtype: ...
        tensor_shape: ...
      }
    }
    outputs: {
      key  : "outputs"
      value: {
        name: "y_outputs_0"
        dtype: DT_FLOAT
        tensor_shape: ...
      }
    }
    method_name: "tensorflow/serving/regress"
  }
}
```

The `inputs` Tensor is equivalent to that of _Classify SignatureDef_, so we proceed
in a similar way.

## Generating the request protobuf files for `half_plus_two` model.

To perform this operation we generate a text-format protobuf `RegressionRequest` using the
the `proto_tfserving.sh` script.

Taking a look to the `GetModelMetadata` response for `half_plus_two` model reveals that
there are more than one _SignatureDef_ for the _Regress_ method:

```
...
signature_def {
  key: "regress_x2_to_y3"
  value {
    inputs {
      key: "inputs"
      ...
    }
    outputs {
      key: "outputs"
      ...
    }
    method_name: "tensorflow/serving/regress"
  }
}
signature_def {
  key: "regress_x_to_y"
  value {
    inputs {
      key: "inputs"
      ...
    }
    outputs {
      key: "outputs"
      ...
      }
    }
    method_name: "tensorflow/serving/regress"
  }
}
signature_def {
  key: "regress_x_to_y2"
  value {
    inputs {
      key: "inputs"
      ...
    }
    outputs {
      key: "outputs"
      ...
    }
    method_name: "tensorflow/serving/regress"
  }
}
...
```

As such, we generate a specific request protobuf for each signature, using an
input file, `half_plus_two.regress.request.input.json` similar to the one used
for the generation of `ClassificationRequest`s:

- Setting `signature_name` to `regress_x_to_y`:

```
bash ../../utils/scripts/proto_tfserving.sh       \
  gen -i half_plus_two.regress.request.input.json \
      -f text                                     \
      -o half_plus_two.regress_x_to_y.request.txt \
      RegressionRequest
```

- Setting `signature_name` to `regress_x_to_y2`:

```
bash ../../utils/scripts/proto_tfserving.sh        \
  gen -i half_plus_two.regress.request.input.json  \
      -f text                                      \
      -o half_plus_two.regress_x_to_y2.request.txt \
      RegressionRequest
```

> The signature `regress_x2_to_y3` does not seem to work with the same
  input data as the 2 other _Regress_ signatures, returning a type error
  (expecting float but string provided). The only difference with the other regressions
  is the type of the `inputs` tensor is `DT_FLOAT` instead of `DT_STRING`. I guess the
  error has something to do with how the Tensor is parsed, but I do not know how to
  exactly generate a correct input. I leave the protobuf generation code below to
  facilitate the reproduction of this error.

- Setting `signature_name` to `regress_x2_to_y3`:

```
bash ../../utils/scripts/proto_tfserving.sh                \
  gen -i half_plus_two.regress_x2_to_y3.request.input.json \
      -f text                                              \
      -o half_plus_two.regress_x2_to_y3.request.txt        \
      RegressionRequest
```

> Note that `mnist` model does not have any _Regress_ signature.

## Querying the serving with a `Classification` request.

We query the serving using `grpc_tfserving.sh`, for each of the regression
signatures of `half_plus_two` model:

- For `regress_x_to_y`:

```
bash ../../utils/scripts/grpc_tfserving.sh                \
  query prediction                                        \
    Regress                                               \
    --in_text half_plus_two.regress_x_to_y.request.txt    \
    --out_json half_plus_two.regress_x_to_y.response.json \
    --out_text half_plus_two.regress_x_to_y.response.txt
```

- For `regress_x_to_y2`:

```
bash ../../utils/scripts/grpc_tfserving.sh                 \
  query prediction                                         \
    Regress                                                \
    --in_text half_plus_two.regress_x_to_y2.request.txt    \
    --out_json half_plus_two.regress_x_to_y2.response.json \
    --out_text half_plus_two.regress_x_to_y2.response.txt
```

> Remember that `regress_x2_to_y3` returns an error.

- For `regress_x2_to_y3`:

```
bash ../../utils/scripts/grpc_tfserving.sh                  \
  query prediction                                          \
    Regress                                                 \
    --in_text half_plus_two.regress_x2_to_y3.request.txt    \
    --out_json half_plus_two.regress_x2_to_y3.response.json \
    --out_text half_plus_two.regress_x2_to_y3.response.txt
```

The output files resulting from these queries are saved in this directory.

- In the case of `regress_x_to_y`, the response returns a `regressions` Tensor
  whose values are the same than those obtained from a _Predict_ request.

- In the case of `regress_x_to_y2`, the response also returns a `regressions`
  but 3 is added to the division, instead of 2. This is expected behaviour
  as we can see in the
  [code](https://github.com/tensorflow/serving/tree/master/tensorflow_serving/servables/tensorflow/testdata/saved_model_half_plus_two.py)
  of the model.