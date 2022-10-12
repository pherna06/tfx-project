# HandleReloadConfigRequest

This operation modifies the model configuration of the serving by adding
or removing models and model versions.

## Handling label reassignment

As we commented before, by default, the serving does not allow to assign
labels to non-loaded model versions. We overcame this restriction by setting
the flag `--allow_version_labels_for_unavailable_models`. However, we cannot
freely swap labels from one version to another. From previous tutorial on
model server configuration:

> Please note that this only applies to new version labels (i.e. ones not
  assigned to a version currently). This is to ensure that during version
  swaps, the server does not prematurely assign the label to the new version,
  thereby dropping all requests destined for that label while the new version
  is loading.

> If you would like to move a label from pointing to version `N` to version
  `N + 1`, you may first submit a config containing version `N` and `N + 1`
  and then submit a config that contains version `N + 1`, the label pointing
  to `N + 1` and no version `N`.

## Reassigning labels in _MNIST_ model

We are going to use the `HandleReloadConfigRequest` operation to:

- Unload _MNIST_ model version `1`.
- Load _MNIST_ model version `4`.
- Reassign labels `early`, `stable` and `canary` to _MNIST_ model versions
  `2`, `3` and `4`, respectively.

We already have versions `2` and `3` loaded in the serving, so reassignment
of labels `early` and `stable` should be possible without taking care of the
previous observation.
For version `4`, however, we must first load it and then assign the `canary`
label to it.

This way, for a __first query__ we do:

- Remove version `1`.
- Keep versions `2` and `3` with respective labels `early` and `stable`.
- Add version `4` (unlabeled).

For the __second query__, we would just keep versions `2`, `3` and `4`, mantaining
the labels of the first two and adding label `canary` to version `4`.

In fact, trying to make a direct modification without following these steps in order
will report an error and maintain the previous model configuration. We can check it
querying the server with this bad request, in `config.request.error.txt`:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    HandleReloadConfigRequest              \
    --in_text config.request.error.txt     \
    -p
```

If we check the serving model status with the following command, you can see that
nothing has changed from the original configuration of the serving:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    GetModelStatus                         \
    --in_text status.request.txt           \
    -p
```

Now, we perform the serving reconfiguration by following the appropiate steps,
using the request messages `config.request.1.txt` and `config.request.2.txt`:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    HandleReloadConfigRequest              \
    --in_text config.request.1.txt         \
    -p
```

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query model                              \
    HandleReloadConfigRequest              \
    --in_text config.request.2.txt         \
    -p
```

Checking the serving status afterwards will report this answer:

```
model_version_status {
  version: 4
  state: AVAILABLE
  status {
  }
}
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
  state: END
  status {
  }
}
```

Note that although version 1 from _MNIST_ model is no longer available (_loaded_),
the serving knows it was once available and keeps record of it.

Finally, we can repeat the inferences we did (by label) with original configuration
of the server.

```
bash ../../utils/scripts/grpc_tfserving.sh          \
  query prediction                                  \
    Classify                                        \
    --in_text prediction/mnist/early.request.txt    \
    --out_json prediction/mnist/early.response.json \
    --out_text prediction/mnist/early.response.txt
```

```
bash ../../utils/scripts/grpc_tfserving.sh           \
  query prediction                                   \
    Classify                                         \
    --in_text prediction/mnist/stable.request.txt    \
    --out_json prediction/mnist/stable.response.json \
    --out_text prediction/mnist/stable.response.txt
```

```
bash ../../utils/scripts/grpc_tfserving.sh           \
  query prediction                                   \
    Classify                                         \
    --in_text prediction/mnist/canary.request.txt    \
    --out_json prediction/mnist/canary.response.json \
    --out_text prediction/mnist/canary.response.txt
```

With the serving reconfiguration, the responses to the current `early` and `stable`
versions shall be identical to those of the previous `stable` and `canary` versions,
respectively. This can be easily checked with the `diff` command:

```
diff prediction/mnist/early.response.txt ../get_model_status/prediction/mnist/stable.response.txt
```

```
diff prediction/mnist/stable.response.txt ../get_model_status/prediction/mnist/canary.response.txt
```