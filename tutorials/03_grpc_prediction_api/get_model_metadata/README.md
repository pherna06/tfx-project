# GetModelMetadata

This operation returns the metadata of a specified model (and version/label) loaded
in the serving `ModelServer`.

- If no version is specified, metadata from the latest (numerical) version will be
  retrieved.
- For now, the only available metadata is for `signature_def`, which we configure in
  `metadata_field` request message field.


## Generating the request protobuf file.

To perform this operation, we generate a text-format protobuf `GetModelMetadataRequest`
using the `proto_tfserving.sh` script.

### For `mnist` model:

We use the script without input file:

```
bash ../../utils/scripts/proto_tfserving.sh \
  gen -f text                               \
      -o mnist.request.txt                  \
      GetModelMetadataRequest
```

And fill in the needed message fields:

```
== Running with Docker...
> Generating 'GetModelMetadataRequest' message...
> Add 'model_spec' (ModelSpec) field? (Yes: any | No 'n'):
>> Generating 'ModelSpec' message...
>> Add 'name' (string) field? (Yes: any | No 'n'):
>>   Input 'name': mnist
>> Add 'version_choice' (oneof) field? (Yes: any | No 'n'): n
>> Add 'signature_name' (string) field? (Yes: any | No 'n'): n
>> No more fields left in 'ModelSpec' message.
> Add 'metadata_field' (repeated string) field? (Yes: any | No 'n'):
>   Add element to 'metadata_field'? (Yes: any | No 'n'):
>     Input element (string): signature_def
>   Add element to 'metadata_field'? (Yes: any | No 'n'): n
> No more fields left in 'GetModelMetadataRequest' message.
> text-format chosen.
Saving text-format protobuf in /home/pherna06/repos/pherna06/tfx-project/tutorials/03_grpc_prediction_api/get_model_metadata/mnist.request.txt
```

...obtaining the `mnist.request.txt` file:

```
model_spec {
  name: "mnist"
}
metadata_field: "signature_def"
```

### For `half_plus_two` model:

For the sake of providing examples, we use the script with an input file,
`half_plus_two.request.input.json`:

```
{
  "model_spec": {
    "name": "half_plus_two",
    "version_choice": {
      "version": 1
    }
  },
  "metadata_field": [
    "signature_def"
  ]
}
```

And we call the script, denying questions to fill in the fields that are not
present in the input file:

```
bash ../../utils/scripts/proto_tfserving.sh \
  gen -i half_plus_two.request.input.json   \
      -f text                               \
      -o half_plus_two.request.txt          \
      GetModelMetadataRequest
```


In the same way, we obtain a `half_plus_two.request.txt` protobuf file with the request:

```
model_spec {
  name: "half_plus_two"
  version {
    value: 1
  }
}
metadata_field: "signature_def"
```

## Querying the serving with a `GetModelMetadata` request.

Now that we have our request configuration files, we just need to use the
`grpc_tfserving.sh` script, which implements the command interface from Python
`query_grpc.py` script.

First of all, we have to query the _Prediction API_, so we use the command chain
`query prediction`. Next, we pass the protobuf request message that the query will
use with the `--in_text` option (there exists a `--in_json` option for json-format
files too). We ask for the output response protobuf both in text and json-format
with the `--out_text` and `--out_json` options (the response to this query will
be long, so we avoid the `-p` optiont that show the response in terminal prompt).

Moreover, the response of this query,
[`GetModelMetadataResponse`](http://github.com/tensorflow/serving/tree/master/tensorflow_serving/apis/get_model_metadata.proto),
contains a `google.protobuf.Any` type field; this means that, for the message to be
displayed correctly, we have to provide the protobuf parser a way of resolving
the type. In this case, we only need to provide the `SignatureDefMap` descriptor,
which we do with the `-d` option.

> In fact, if you check it, the descriptor option is irrelevant on the resulting
  output files. This did not happen in a previous implementation and I think
  that the difference with this implementation is the way the different protobuf
  modules were imported. Now, they are all imported globally in its respective
  file, while in the previous implementation, they were imported locally inside
  the methods that needed them. This way, I think that now the protobuf parser
  has access to the descriptors as they are imported globally; as a result,
  using a descriptor pool should be irrelevant.

Finally, we specify the type of query, `GetModelMetadata`, and, for the `half_plus_two`
model we are left with:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query prediction                         \
    GetModelMetadata                       \
    --in_text half_plus_two.request.txt    \
    --out_json half_plus_two.response.json \
    --out_text half_plus_two.response.txt  \
    -d SignatureDefMap
```

While for the `mnist` model we use:

```
bash ../../utils/scripts/grpc_tfserving.sh \
  query prediction                         \
    GetModelMetadata                       \
    --in_text mnist.request.txt    \
    --out_json mnist.response.json \
    --out_text mnist.response.txt  \
    -d SignatureDefMap
```

The output files resulting from these queries are saved in this directory. It is recommended
to take a look at them, as they describe the operations available in the model, which we will
query with other gRPC API operations like `Predict`, `Classify` or `Regress`.