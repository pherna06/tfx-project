# GetModelStatus

This operation returns the status of the different versions of a model.
If no version is specified, status from all the known versions of the
model will be retrieved.

## Retrieving the status of existing models in serving.

In our serving, models _half\_plus\_two_ and _MNIST_ are both loaded.
To check the status of them both with a `GetModelStatus` query we have
to generate a `GetModelStatusRequest` message for each model. To do that,
we use `proto_tfserving.sh` utility. For example, something like:

```
bash ../../utils/scripts/proto_tfserving.sh \
  gen -o example_model.request.txt          \
      -f text                               \
      GetModelStatusRequest
```

This way, we get both protobuf `GetModelStatusRequest` files:

- For _half\_plus\_two_, in `half_plus_two.request.txt`:

```
model_spec {
  name: "half_plus_two"
}
```

- For _MNIST_, in `mnist.request.txt`:

```
model_spec {
  name: "mnist"
}
```

Now, we just need to make use of `grpc_serving.sh` script to query the
serving with `GetModelStatus` for each model:

### For _half\_plus\_two_.

We query with:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    GetModelStatus                         \
    --in_text half_plus_two.request.txt    \
    --out_json half_plus_two.response.json \
    --out_text half_plus_two.response.txt
```

And obtain the response:

```
model_version_status {
  version: 1
  state: AVAILABLE
  status {
  }
}
```

As we expected, the only version of the model is available.

### For _MNIST_.

We query with:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    GetModelStatus                         \
    --in_text mnist.request.txt            \
    --out_json mnist.response.json         \
    --out_text mnist.response.txt
```

And obtain the response:

```
model_version_status {
  version: 3
  state: AVAILABLE
  status {
  }
}
model_version_status {
  version: 2
  state: AVAILABLE
  status {
  }
}
model_version_status {
  version: 1
  state: AVAILABLE
  status {
  }
}
```

As we specified in the initial server model configuration, versions `1, 2, 3`
are available.

## Making inferences using version labels.

As labels where assigned to the different versions, we are going to see that
we can query each version as in the previous tutorial by using its label to
identify it.

### For _half\_plus\_two_.

We query version `stable` with a `Predict` request. We reuse the `PredictRequest`
message from the previous tutorial, adding the field `version_label` to it. This
message is saved in file `half_plus_two/stable.request.txt`. Next, we just query
with _Prediction API_ as usual:

```
bash ../../utils/scripts/grpc_tfserving.sh                   \
  query prediction                                           \
    Predict                                                  \
    --in_text prediction/half_plus_two/stable.request.txt    \
    --out_json prediction/half_plus_two/stable.response.json \
    --out_text prediction/half_plus_two/stable.response.txt
```

Query is answered without errors, meaning that the label reference has worked.

### For _MNIST_.

In this case we have 3 different versions, `early`, `stable` and `canary`,
which are sequentially more trained versions of the same model, respectively.
This way, inferences over each version with the same input will return different
results.

In this case, we make `Classify` queries and obtain the `ClassifyRequest` messages
for each version in the same way as we did with _half\_plus\_two_ previously.

Finally, we query each version as usual:

- For `early`:

```
bash ../../utils/scripts/grpc_tfserving.sh          \
  query prediction                                  \
    Classify                                        \
    --in_text prediction/mnist/early.request.txt    \
    --out_json prediction/mnist/early.response.json \
    --out_text prediction/mnist/early.response.txt
```

- For `stable`:

```
bash ../../utils/scripts/grpc_tfserving.sh           \
  query prediction                                   \
    Classify                                         \
    --in_text prediction/mnist/stable.request.txt    \
    --out_json prediction/mnist/stable.response.json \
    --out_text prediction/mnist/stable.response.txt
```

- For `canary`:

```
bash ../../utils/scripts/grpc_tfserving.sh           \
  query prediction                                   \
    Classify                                         \
    --in_text prediction/mnist/canary.request.txt    \
    --out_json prediction/mnist/canary.response.json \
    --out_text prediction/mnist/canary.response.txt
```

All queries return without error and we can check in the output files that
the results are different for each version.