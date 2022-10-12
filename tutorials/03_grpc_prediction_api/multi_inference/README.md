# MultiInference

This operation is used to query the serving with a series of different signatures
from the same model with the same input data. The only signature
types allowed are _Classify_ and _Regress_ methods. As such, the definition of
a `MultiInferenceRequest` message is given by:

```
// Inference request such as classification, regression, etc...
message InferenceTask {
  // Model Specification. If version is not specified, will use the latest
  // (numerical) version.
  // All ModelSpecs in a MultiInferenceRequest must access the same model name.
  ModelSpec model_spec = 1;

  // Signature's method_name. Should be one of the method names defined in
  // third_party/tensorflow/python/saved_model/signature_constants.py.
  // e.g. "tensorflow/serving/classify".
  string method_name = 2;
}

// Inference request containing one or more requests.
message MultiInferenceRequest {
  // Inference tasks.
  repeated InferenceTask tasks = 1;

  // Input data.
  Input input = 2;
}
```

## Generating the request protobuf file for multi inference.

To perform this operation we generate a text-format protobuf `MultiInference` using the
the `proto_tfserving.sh` script.

We are gonna query all the possible _Classify_ and _Regress_ signatures from `half_plus_two`
(the working ones, at least) seen up to now, this is:

- 1 _Classify_ signature named `classify_x_to_y`,
- 2 _Regress_ signatures named `regress_x_to_y` and `regress_x_to_y2`.

We call the generation script with input file `half_plus_two.request.input.json`:

```
bash ../../utils/scripts/proto_tfserving.sh \
  gen -i half_plus_two.request.input.json   \
      -f text                               \
      -o half_plus_two.request.txt          \
      MultiInferenceRequest
```

## Querying the serving with a `Classification` request.

We query the serving using `grpc_tfserving.sh`:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query prediction                         \
    MultiInference                         \
    --in_text half_plus_two.request.txt    \
    --out_json half_plus_two.response.json \
    --out_text half_plus_two.response.txt
```

The output files resulting from the query are saved in this directory.