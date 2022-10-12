# Classify

This operation is used for performing a classification inference of a model.
[`Classify SignatureDef`](https://www.tensorflow.org/tfx/serving/signature_defs#classification_signaturedef)
supports structured calls to TensorFlow Serving's Classification API. These
prescribe that there must be an `inputs` Tensor, and that there are 2 optional
output Tensors: `classes` and `scores`, at least one of which must be present.
For example:

```
signature_def: {
  key  : "my_classification_signature"
  value: {
    inputs: {
      key  : "inputs"
      value: {
        name: "tf_example:0"
        dtype: DT_STRING
        tensor_shape: ...
      }
    }
    outputs: {
      key  : "classes"
      value: {
        name: "index_to_string:0"
        dtype: DT_STRING
        tensor_shape: ...
      }
    }
    outputs: {
      key  : "scores"
      value: {
        name: "TopKV2:0"
        dtype: DT_FLOAT
        tensor_shape: ...
      }
    }
    method_name: "tensorflow/serving/classify"
  }
}
```

In particular, the `inputs` Tensor is comprised of the so called protobuf
[`Examples`](http://github.com/tensorflow/tensorflow/tree/master/tensorflow/core/example/example.proto),
which are, at the same time, conformed by protobuf
[`Features`](http://github.com/tensorflow/tensorflow/tree/master/tensorflow/core/example/feature.proto),
each feature representing a list of data. Analizing from up to down:

- `inputs` message has field `example_list` (_ExampleList_).
- `example_list` message has field `examples` (repeated _Example_).
- Each _Example_ message has field `features` (_Features_).
- `features` message has field `feature` (_map\<string, Feature\>_).
- Each _Feature_ message has field `kind` (_oneof_).
- `kind` can be `bytes_list` (repeated _bytes_ `value`), `float_list` (repeated _float_ `value`) or
  `int64_list` (repeated _int64_ `value`).

In conclusion, each example in `example_list` must contain an only sample of for model
inference. A sample can have different features, though in our example models
(`half_plus_two` and `mnist`) each sample has only one feature. This way:

- For `half_plus_two`, each example would have feature `x` followed by a 1 value list
  (i.e. `[1.0]`).
- For `mnist`, each example would have feature `x` followed by an image represented by
  a `28 x 28` values list.

> The features naming does not seem to appear in `GetModelMetadata` responses. However, in case
  of a giving a wrong name, the GRPC query fails and returns an error indicating the names
  of the expected features (which, in both cases seem to be `x`).

## Generating the request protobuf file for `half_plus_two` model.

To perform this operation we generate a text-format protobuf `ClassificationRequest` using the
the `proto_tfserving.sh` script.

Now, to query the `half_plus_two` model, we take a look to the response of the model to
the `GetModelMetadata` query:

```
...
signature_def {
  key: "classify_x_to_y"
  value {
    inputs {
      key: "inputs"
      value {
        name: "tf_example:0"
        dtype: DT_STRING
        tensor_shape {
          unknown_rank: true
        }
      }
    }
    outputs {
      key: "scores"
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
    method_name: "tensorflow/serving/classify"
  }
}
...
```

As we can see, the only signature that uses a _Classify_ inference type is that with
the name `classify_x_to_y`. It takes an only tensor named `inputs` (as expected), and
as output, it generates an only tensor named `scores`.

With this analysis, we call the script to generate the request using
`half_plus_two.classify_x_to_y.request.input.json` as input file:

```
bash ../../utils/scripts/proto_tfserving.sh               \
  gen -i half_plus_two.classify_x_to_y.request.input.json \
      -f text                                             \
      -o half_plus_two.classify_x_to_y.request.txt        \
      ClassificationRequest
```

...obtaining the `half_plus_two.classify_x_to_y.request.json` file:

> Note that the structure of both the input file and the probobuf file is relatively
  complex due to the depth of subsequent submessages.

## Generating the request protobuf file for `mnist` model.

In case of the `mnist` model (which resembles a more usual model than `half_plus_two`),
we include a specific `ClassificationRequest` for `mnist` as we did previously in the
_Predict_ service. It asks for the number of examples and generates them randomly too.

Besides, the signature name for the only _Classify_ method in the model is called
`serving_default`. Finally, we call the script:

```
bash ../../utils/scripts/proto_tfserving.sh       \
  gen -f text                                     \
      -o mnist.serving_default.request.txt        \
      mnist:serving_default:ClassificationRequest
```

...setting the number of examples to 5, the `mnist.serving_default.request.txt` protobuf
file is generated.

## Querying the serving with a `Classification` request.

We query the serving using `grpc_tfserving.sh`:

For `half_plus_two`:

```
bash ../../utils/scripts/grpc_tfserving.sh                 \
  query prediction                                         \
    Classify                                               \
    --in_text half_plus_two.classify_x_to_y.request.txt    \
    --out_json half_plus_two.classify_x_to_y.response.json \
    --out_text half_plus_two.classify_x_to_y.response.txt
```

For `mnist`:

```
bash ../../utils/scripts/grpc_tfserving.sh         \
  query prediction                                 \
    Classify                                       \
    --in_text mnist.serving_default.request.txt    \
    --out_json mnist.serving_default.response.json \
    --out_text mnist.serving_default.response.txt
```

The output files resulting from these queries are saved in this directory.

- In the case of `half_plus_two` model, the response only gives Tensor
  `scores` for each sample. In particular, these values are the same
  obtained from the _Predict_ request.

- In the case of `mnist` model, the response gives both Tensors, `scores`
  and `labels`, for each sample. In particular, for each _label_ (class),
  its _score_ (probability for the class) is given, so each sample can
  be classified to a label.