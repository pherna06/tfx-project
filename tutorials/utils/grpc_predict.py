import grpc
import tensorflow as tf

from tensorflow_serving.apis import prediction_service_pb2_grpc

def get_predict_request(
        model_spec    ,
        inputs        ,
        output_filter ):

    from tensorflow_serving.apis import predict_pb2
    request = predict_pb2.PredictRequest()

    # ModelSpec
    request.model_spec.name = model_spec['name']
    if 'version' in model_spec:
        request.model_spec.version = model_spec['version']
    if 'version_label' in model_spec:
        request.model_spec.version_label = model_spec['version_label']
    if 'signature_name' in model_spec:
        request.model_spec.signature_name = model_spec['signature_name']

    # Inputs
    for alias in inputs:
        request.inputs[alias].CopyFrom(
                tf.make_tensor_proto(inputs[alias]) )

    # OutputFilter
    for alias in output_filter:
        request.output_filter.append(alias)

    return request

def get_predict_result(
        response ):

    result = {}

    # ModelSpec
    result['model_spec'] = {}
    result_model_spec = response.model_spec
    result['model_spec']['name']           = result_model_spec.name
    result['model_spec']['version']        = result_model_spec.version
    result['model_spec']['version_label']  = result_model_spec.version_label
    result['model_spec']['signature_name'] = result_model_spec.signature_name

    # Outputs
    result['outputs'] = {}
    result_outputs = response.outputs
    for alias in result_outputs:
        result['outputs'][alias] = result_outputs[alias].float_val

    return result

def do_predict(
        stub          ,
        model_spec    ,
        inputs        ,
        output_filter ):

    request = get_predict_request(model_spec, inputs, output_filter)

    # >> Call Service <<
    rpc = stub.Predict(request, 5.0)
    
    # Print result
    exception = rpc.exception()
    if exception:
        print(exception)
    else:
        result = get_prediction_result(rpc.result())
        
        print(result)

def set_classification_regression_request(
        request    ,
        model_spec ,
        context    ,
        examples   ):

    # ModelSpec
    request.model_spec.name = model_spec['name']
    if 'version' in model_spec:
        request.model_spec.version = model_spec['version']
    if 'version_label' in model_spec:
        request.model_spec.version_label = model_spec['version_label']
    if 'signature_name' in model_spec:
        request.model_spec.signature_name = model_spec['signature_name']

    # Examples (and context)
    if context:
        context_example = request.input.example_list_with_context.context
        for feat in context:
            ## context[feat] is list
            content_example.features.feature[feat].float_list.value.extend(context[feat])
        for ex in examples:
            example = request.input.example_list_with_context.examples.add()
            for feat in ex:
                example.features.feature[feat].float_list.value.extend(ex[feat])
    else:
        for ex in examples:
            example = request.input.example_list.examples.add()
            for feat in ex:
                example.features.feature[feat].float_list.value.extend(ex[feat])

def get_classification_request(
        model_spec ,
        context    ,
        examples   ):

    from tensorflow_serving.apis import classification_pb2
    request = classification_pb2.ClassificationRequest()

    set_classification_regression_request(
            request    ,
            model_spec ,
            context    ,
            examples   )

    return request

def get_classification_result(
        response ):

    result = {}

    # ModelSpec
    result['model_spec'] = {}
    result_model_spec = response.model_spec
    result['model_spec']['name']           = result_model_spec.name
    result['model_spec']['version']        = result_model_spec.version
    result['model_spec']['version_label']  = result_model_spec.version_label
    result['model_spec']['signature_name'] = result_model_spec.signature_name

    # ClassificationResult
    result['classifications'] = []
    result_classifications = grpc.result().result.classifications
    for classification in result_classifications:
        result['classifications'].append({})
        for cl in classification.classes:
            result['classifications'][-1]['label'] = cl.label
            result['classifications'][-1]['score'] = cl.score

    print(result)


def do_classify(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_classification_request(model_spec, context, examples)

    # >> Call Service <<
    rpc = stub.Classify(request, 5.0)

    exception = rpc.exception()
    if exception:
        print(exception)
    else:
        result = get_classification_result(rpc.result())

        print(result)

def get_regression_request(
        model_spec ,
        context    ,
        examples   ):

    from tensorflow_serving.apis import regression_pb2
    request = regression_pb2.RegressionRequest()

    set_classification_regression_request(
            request    ,
            model_spec ,
            context    ,
            examples   )

    return request

def get_regression_result(
        response ):

    result = {}

    # ModelSpec
    result['model_spec'] = {}
    result_model_spec = response.model_spec
    result['model_spec']['name']           = result_model_spec.name
    result['model_spec']['version']        = result_model_spec.version
    result['model_spec']['version_label']  = result_model_spec.version_label
    result['model_spec']['signature_name'] = result_model_spec.signature_name

    # RegressionResult
    result['regressions'] = []
    result_regressions = grpc.result().result.regressions
    for regression in result_regressions:
        result['regressions'].append(regression.value)

    print(result)

def do_regress(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_regression_request(model_spec, context, examples)

    # >> Call Service <<
    rpc = stub.Regress(request, 5.0)

    exception = rpc.exception()
    if exception:
        print(exception)
    else:
        result = get_regression_result(rpc.result())

        print(result)

def get_multi_inference_request(
        tasks    ,
        context  ,
        examples ):

    from tensorflow_serving.apis import inference_pb2
    multi_request = inference_pb2.MultiInferenceRequest()

    # InferenceTasks
    for task in tasks:
        request = multi_request.tasks.add()
        
        # ModelSpec
        model_spec = task['model_spec']
        request.model_spec.name = model_spec['name']
        if 'version' in model_spec:
            request.model_spec.version = model_spec['version']
        if 'version_label' in model_spec:
            request.model_spec.version = model_spec['version_label']
        if 'signature_name' in model_spec:
            request.model_spec.signature_name = model_spec['signature_name']

        # MethodName
        request.method_name = task['method_name']

    # Examples (and context)
    if context:
        context_example = multi_request.input.example_list_with_context.context
        for feat in context:
            ## context[feat] is list
            content_example.features.feature[feat].float_list.value.extend(context[feat])
        for ex in examples:
            example = multi_request.input.example_list_with_context.examples.add()
            for feat in ex:
                example.features.feature[feat].float_list.value.extend(ex[feat])
    else:
        for ex in examples:
            example = multi_request.input.example_list.examples.add()
            for feat in ex:
                example.features.feature[feat].float_list.value.extend(ex[feat])

def get_multi_inference_results(
        response ):

    results = []

    for inf_result in response.results:
        result = {}
        if inf_result.HasField('classification_result'):
            result = get_classification_result(inf_result.classification_result)
        if inf_result.HasField('regression_result'):
            result = get_regression_result(inf_result.regression_result)

        results.append(result)

    return results

def do_multi_inference(
        stub     ,
        tasks    ,
        context  ,
        examples ):

    request = get_multi_inference_request(tasks, context, examples)

    rpc = stub.MultiInference(request, 5.0)

    exception = rpc.exception()
    if exception:
        print(exception)
    else:
        results = get_multi_inference_results(rpc.result())

        print(results)

def get_get_model_metadata_request(
        model_spec      ,
        metadata_fields ):

    from tensorflow_serving.apis import get_model_metadata_pb2
    request = get_model_metadata_pb2.GetModelMetadataRequest()

    # ModelSpec
    request.model_spec.name = model_spec['name']
    if 'version' in model_spec:
        request.model_spec.version = model_spec['version']
    if 'version_label' in model_spec:
        request.model_spec.version_label = model_spec['version_label']
    if 'signature_name' in model_spec:
        request.model_spec.signature_name = model_spec['signature_name']

    # MetadataFields
    for field in metadata_fields:
        request.metadata_fields.append(field)

    return request

def get_tensor_info_result(
        tensor_info):

    result = {}

    # Encoding
    if tensor_info.HasField('name'):
        result['name'] = tensor_info.name
    if tensor_info.HasField('coo_sparse'):
        result['values_tensor_name']      = tensor_info.coo_sparse.values_tensor_name
        result['indices_tensor_name']     = tensor_info.coo_sparse.indices_tensor_name
        result['dense_shape_tensor_name'] = tensor_info.coo_sparse.dense_shape_tensor_name
    if tensor_info.HasField('composite_tensor'):
        result['composite_tensor'] = []
        ## do not parse 'type_spec'
        for tensor_comp in tensor_info.composite_tensor.components:
            result['composite_tensor'].append(get_tensor_info_result(tensor_comp)

    # DataType (enum)
    result['dtype'] = tensor_info.dtype

    # TensorShape
    result['tensor_shape']['dim'] = []
    for dim in tensor_info.tensor_shape.dim:
        dim_dict = {
            'size': dim.size ,
            'name': dim.name }
        result['tensor_shape']['dim'].append(dim_dict)

    result['tensor_shape']['unknown_rank'] = tensor_info.tensor_shape.unknown_rank

    return result

def get_get_model_metadata_result(
        response ):

    result = {}

    # ModelSpec
    result['model_spec'] = {}
    result_model_spec = response.model_spec
    result['model_spec']['name']           = result_model_spec.name
    result['model_spec']['version']        = result_model_spec.version
    result['model_spec']['version_label']  = result_model_spec.version_label
    result['model_spec']['signature_name'] = result_model_spec.signature_name

    # Metadata
    result['metadata'] = {}
    result_metadata = response.metadata
    for field in result_metadata:
        result['metadata'][field] = {}

        # Inputs
        result['metadata'][field]['inputs'] = {}
        inputs = result['metadata'][field]['inputs']
        for alias in result_metadata[field].inputs:
            tensor_info = result_metadata[field].inputs[alias]
            inputs[alias] = get_tensor_info_result(tensor_info)

        # Outputs
        result['metadata'][field]['outputs'] = {}
        outputs = result['metadata'][field]['outputs']
        for alias in result_metadata[field].outputs:
            tensor_info = result_metadata[field].outputs[alias]
            outputs[alias] = get_tensor_info_result(tensor_info)

        # MethodName
        result['metadata'][field]['method_name'] = result_metadata[field].method_name

    return result

def do_get_model_metadata(
        stub            ,
        model_spec      ,
        metadata_fields ):

    request = get_get_model_metadata_request(model_spec, metadata_fields)

    rpc = stub.GetModelMetadata(request, 5.0)

    exception = rpc.exception()
    if exception:
        print(exception)
    else:
        result = get_get_model_metadata_result(rpc.result())

        print(result)



############################

def get_parser():
    desc = "A script that runs a gRPC query to a TensorFlow serving."
    desc += " This is an example script, which implements functionality "
    desc += " ONLY for float data types."
    parser = argparse.ArgumentParser(description=desc)

    query_help = "Path to JSON query file"
    parser.add_argument(
            'query', metavar='QUERY', help=query_help,
            type=str )

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    with open(args.query) as json_file:
        query = json.load(json_file)

    # gRPC server
    if 'server' not in query:
        print('ERROR: gRPC server not specified')
        return -1

    channel = grpc.insecure_channel(query['server'])
    stub = prediction_service_pb2_grpc.PredictionService(channel)

    # Op parsing
    if 'op' not in query:
        print('ERROR: operation not specified.')
        return -1

    if   query['op'] == 'Predict':
        do_predict(
                stub                ,
                query['model_spec'] ,
                query['inputs']     )

    elif query['op'] == 'Classify':
        do_classify(
                stub                ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'Regress':
        do_regress(
                stub                ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'MultiInference':
        do_multi_inference(
                stub              ,
                query['tasks']    ,
                query['context']  ,
                query['examples'] )

    elif query['op'] == 'GetModelMetadata':
        do_get_model_metadata(
                stub                     ,
                query['model_spec']      ,
                query['metadata_fields'] )

    else:
        print('ERROR: unknown operation')
        return -1

if __name__ == '__main__':
    main()
