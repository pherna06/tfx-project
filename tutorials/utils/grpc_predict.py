import argparse
import json

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
    model_spec = response.model_spec
    result['model_spec']['name']           = model_spec.name
    result['model_spec']['version']        = model_spec.version
    result['model_spec']['version_label']  = model_spec.version_label
    result['model_spec']['signature_name'] = model_spec.signature_name

    # Outputs
    result['outputs'] = {}
    outputs = response.outputs
    for alias in outputs:
        result['outputs'][alias] = outputs[alias].float_val

    return result

def do_predict(
        stub          ,
        model_spec    ,
        inputs        ,
        output_filter ):

    request = get_predict_request(model_spec, inputs, output_filter)

    # >> Call Service <<
    response = stub.Predict(request, 5.0)
    
    # Print result
    result = get_prediction_result(response)
    return result

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
    model_spec = response.model_spec
    result['model_spec']['name']           = model_spec.name
    result['model_spec']['version']        = model_spec.version
    result['model_spec']['version_label']  = model_spec.version_label
    result['model_spec']['signature_name'] = model_spec.signature_name

    # ClassificationResult
    result['classifications'] = []
    classifications = response.result.classifications
    for classification in classifications:
        result['classifications'].append({})
        for cl in classification.classes:
            result['classifications'][-1]['label'] = cl.label
            result['classifications'][-1]['score'] = cl.score

    return result


def do_classify(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_classification_request(model_spec, context, examples)

    # >> Call Service <<
    response = stub.Classify(request, 5.0)

    result = get_classification_result(response)
    return result

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
    model_spec = response.model_spec
    result['model_spec']['name']           = model_spec.name
    result['model_spec']['version']        = model_spec.version
    result['model_spec']['version_label']  = model_spec.version_label
    result['model_spec']['signature_name'] = model_spec.signature_name

    # RegressionResult
    result['regressions'] = []
    regressions = response.result.regressions
    for regression in regressions:
        result['regressions'].append(regression.value)

    return result

def do_regress(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_regression_request(model_spec, context, examples)

    # >> Call Service <<
    response = stub.Regress(request, 5.0)

    result = get_regression_result(response)
    return results

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

    response = stub.MultiInference(request, 5.0)

    results = get_multi_inference_results(response)
    return results

def get_get_model_metadata_request(
        model_spec      ,
        metadata_field  ):

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
    for field in metadata_field:
        request.metadata_field.append(field)

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
            result['composite_tensor'].append (get_tensor_info_result(tensor_comp) )

    # DataType (enum)
    result['dtype'] = tensor_info.dtype

    # TensorShape
    result['tensor_shape'] = {}
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
    model_spec = response.model_spec
    result['model_spec']['name']           = model_spec.name
    result['model_spec']['version']        = model_spec.version
    result['model_spec']['version_label']  = model_spec.version_label
    result['model_spec']['signature_name'] = model_spec.signature_name

    # Metadata
    result['metadata'] = {}
    metadata = response.metadata
    for field in metadata:
        if field != 'signature_def':
            print('unknown metadata field:', field)
            continue

        ## TODO getter method for SignatureDefMap
        from tensorflow_serving.apis import get_model_metadata_pb2
        signature_map = get_model_metadata_pb2.SignatureDefMap()
        if metadata[field].Is(signature_map.DESCRIPTOR):
            metadata[field].Unpack(signature_map)

        result['metadata'][field] = {}

        for signature_key in signature_map.signature_def:
            result['metadata'][field][signature_key] = {}
            signature = result['metadata'][field][signature_key]
            response_signature = signature_map.signature_def[signature_key]

            # Inputs
            signature['inputs'] = {}
            for alias in response_signature.inputs:
                tensor_info = response_signature.inputs[alias]
                signature['inputs'][alias] = get_tensor_info_result(tensor_info)

            # Outputs
            signature['outputs'] = {}
            for alias in response_signature.outputs:
                tensor_info = response_signature.outputs[alias]
                signature['outputs'][alias] = get_tensor_info_result(tensor_info)

            # MethodName
            signature['method_name'] = response_signature.method_name

    return result

def do_get_model_metadata(
        stub            ,
        model_spec      ,
        metadata_field  ):

    request = get_get_model_metadata_request(model_spec, metadata_field)

    response = stub.GetModelMetadata(request, 5.0)

    result = get_get_model_metadata_result(response)
    return result


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

    output_help = "Path to JSON query result file"
    parser.add_argument(
            '-o', '--output', metavar='output', help=output_help,
            type=str, default=None )

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
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    # Op parsing
    if 'op' not in query:
        print('ERROR: operation not specified.')
        return -1

    if   query['op'] == 'Predict':
        result = do_predict(
                stub                ,
                query['model_spec'] ,
                query['inputs']     )

    elif query['op'] == 'Classify':
        result = do_classify(
                stub                ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'Regress':
        result = do_regress(
                stub                ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'MultiInference':
        result = do_multi_inference(
                stub              ,
                query['tasks']    ,
                query['context']  ,
                query['examples'] )

    elif query['op'] == 'GetModelMetadata':
        result = do_get_model_metadata(
                stub                    ,
                query['model_spec']     ,
                query['metadata_field'] )

    else:
        print('ERROR: unknown operation')
        return -1

    if args.output:
        with open(args.output, 'w') as outjson:
            json.dump(result, outjson, default=str, indent=4)
    else:
        print(result)


if __name__ == '__main__':
    main()
