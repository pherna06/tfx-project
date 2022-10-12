import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import argparse
import json

import grpc
import tensorflow as tf

from tensorflow_serving.apis import prediction_service_pb2_grpc
from google.protobuf import json_format, text_format


# ModelSpec #

def set_model_spec(
        message    ,
        model_spec ):

    if 'name' in model_spec:
        message.name = model_spec['name']
    if 'version' in model_spec:
        message.version.value = model_spec['version']
    if 'version_label' in model_spec:
        message.version_label = model_spec['version_label']
    if 'signature_name' in model_spec:
        message.signature_name = model_spec['signature_name']

def parse_model_spec(
        model_spec ):

    parsed = {}

    parsed['name']           = model_spec.name
    parsed['version']        = model_spec.version.value
    parsed['version_label']  = model_spec.version_label
    parsed['signature_name'] = model_spec.signature_name

    return parsed

### ### ### ###

# TensorProto #

def set_tensor_proto(
        message      ,
        tensor_proto ):

    message.CopyFrom( tf.make_tensor_proto(tensor_proto) )

def parse_tensor_proto(
        tensor_proto ):

    return tensor_proto.float_val

### ### ### ###

# tensorflow.serving.Input #

def set_tensorflow_serving_input(
        message  ,
        context  ,
        examples ):

    # ExampleListWithContext
    if context:
        message_context = message.example_list_with_context.context
        for feature in message_context:
            ## context[feature] is list
            message_context.features.feature[feature].float_list.value.extend(context[feature])
        for example in examples:
            message_example = message.example_list_with_context.examples.add()
            for feature in message_example:
                ## exapmle[feat] is list
                message_example.features.feature[feature].float_list.value.extend(example[feature])
    # ExampleList
    else:
        for example in examples:
            message_example = message.example_list.examples.add()
            for feature in example:
                ## ex[feat] is list
                message_example.features.feature[feature].float_list.value.extend(example[feature])


# ClassificationRequest | RegressionRequest #

def set_classification_regression_request(
        request    ,
        model_spec ,
        context    ,
        examples   ):

    # ModelSpec
    set_model_spec(request.model_spec, model_spec)

    # Examples (and context)
    set_tensorflow_serving_input(request.input, context, examples)

### ### ### ###

# Classifications #

def parse_classifications(
        classifications ):

    parsed = []

    for classification in classifications:
        parsed.append({})
        for msg_class in classification.classes:
            parsed[-1]['label'] = msg_class.label
            parsed[-1]['score'] = msg_class.score

    return parsed

### ### ### ###

# TensorInfo #

def parse_tensor_info(
        tensor_info ):

    parsed = {}

    # Encoding
    if tensor_info.HasField('name'):
        parsed['name'] = tensor_info.name
    if tensor_info.HasField('coo_sparse'):
        parsed['values_tensor_name']      = tensor_info.coo_sparse.values_tensor_name
        parsed['indices_tensor_name']     = tensor_info.coo_sparse.indices_tensor_name
        parsed['dense_shape_tensor_name'] = tensor_info.coo_sparse.dense_shape_tensor_name
    if tensor_info.HasField('composite_tensor'):
        parsed['composite_tensor'] = []
        ## do not parse 'type_spec'
        for tensor_comp in tensor_info.composite_tensor.components:
            parsed['composite_tensor'].append (parse_tensor_info(tensor_comp) )

    # DataType (enum)
    parsed['dtype'] = tensor_info.dtype

    # TensorShape
    parsed['tensor_shape'] = {}
    parsed['tensor_shape']['dim'] = []
    for dim in tensor_info.tensor_shape.dim:
        dim_dict = {
            'size': dim.size ,
            'name': dim.name }
        parsed['tensor_shape']['dim'].append(dim_dict)

    parsed['tensor_shape']['unknown_rank'] = tensor_info.tensor_shape.unknown_rank

    return parsed

### ### ### ###

# SignatureDef #

def parse_signature_def(
        signature_def ):

    parsed = {}

    # Inputs
    parsed['inputs'] = {}
    for alias in signature_def.inputs:
        tensor_info = signature_def.inputs[alias]
        parsed['inputs'][alias] = parse_tensor_info(tensor_info)

    # Outputs
    parsed['outputs'] = {}
    for alias in signature_def.outputs:
        tensor_info = signature_def.outputs[alias]
        parsed['outputs'][alias] = parse_tensor_info(tensor_info)

    # MethodName
    parsed['method_name'] = signature_def.method_name

    return parsed

### ### ### ###

### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###




# Classify #

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

def parse_classification_result(
        response      ,
        multi = False ):

    parsed = {}

    # ModelSpec
    parsed['model_spec'] = parse_model_spec(response.model_spec)

    # ClassificationResult
    if multi:
        parsed['classifications'] = parse_classifications(response.classification_result.classifications)
    else:
        parsed['classifications'] = parse_classifications(response.result.classifications)

    return parsed


def do_classify(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_classification_request(model_spec, context, examples)

    # >> Call Service <<
    response = stub.Classify(request)

    result = parse_classification_result(response)
    return result

### ### ### ###




# Regress #

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

def parse_regression_result(
        response      ,
        multi = False ):

    parsed = {}

    # ModelSpec
    parsed['model_spec'] = parse_model_spec(response.model_spec)

    # RegressionResult
    parsed['regressions'] = []

    if multi:
        regressions = response.regression_result.regressions
    else:
        regressions = response.result.regressions

    for regression in regressions:
        parsed['regressions'].append(regression.value)

    return parsed

def do_regress(
        stub          ,
        model_spec    ,
        context       ,
        examples      ):

    request = get_regression_request(model_spec, context, examples)

    # >> Call Service <<
    response = stub.Regress(request)

    result = parse_regression_result(response)
    return result

### ### ### ###



# MultiInference #

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
        set_model_spec(request.model_spec, task['model_spec'])

        # MethodName
        request.method_name = task['method_name']

    # Examples (and context)
    set_tensorflow_serving_input(multi_request.input, context, examples)

    return multi_request

def parse_multi_inference_results(
        response ):

    parsed = []

    for result in response.results:
        if result.HasField('classification_result'):
            parsed.append( parse_classification_result(result, multi=True) )

        if result.HasField('regression_result'):
            parsed.append( parse_regression_result(result, multi=True) )

    return parsed

def do_multi_inference(
        stub     ,
        tasks    ,
        context  ,
        examples ):

    request = get_multi_inference_request(tasks, context, examples)

    response = stub.MultiInference(request)

    results = parse_multi_inference_results(response)
    return results

### ### ### ###

### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###

# GetModelMetadata #

def do_get_model_metadata(
        stub         ,
        request_dict ):
    
    from tensorflow_serving.apis import get_model_metadata_pb2

    request = json_format.ParseDict(
            request_dict ,
            get_model_metadata_pb2.GetModelMetadataRequest() )

    response = stub.GetModelMetadata(request)

    from google.protobuf import descriptor_pool
    pool = descriptor_pool.Default()
    pool.AddDescriptor( get_model_metadata_pb2.SignatureDefMap.DESCRIPTOR)

    return response, pool

def do_predict(
        stub         ,
        request_dict ):
    
    from tensorflow_serving.apis import predict_pb2

    request = json_format.ParseDict(
            request_dict ,
            predict_pb2.PredictRequest() )

    response = stub.Predict(request)

    return response

### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###




def get_parser():
    desc = "A script that runs a query to a TensorFlow Serving gRPC Predict API."
    parser = argparse.ArgumentParser(description=desc)

    query_help = "Path to JSON query file"
    parser.add_argument(
            'query', metavar='QUERY', help=query_help,
            type=str )

    print_help = "Set this flag to print message in terminal."
    parser.add_argument(
            '-p', '--print', dest='print', help=print_help,
            action='store_true' )

    json_out_help =  "Path to JSON file where response message will be saved "
    json_out_help += "in Protobuf json-format."
    parser.add_argument(
            '-j', '--json_output', metavar='json_output', help=json_out_help,
            type=str, default=None )

    text_out_help =  "Path to text file where response message will be saved "
    text_out_help += "in Protobuf text-format."
    parser.add_argument(
            '-t', '--text_output', metavar='text_output', help=text_out_help,
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

    pool = None
    if   query['op'] == 'GetModelMetadata':
        response, pool = do_get_model_metadata(
                stub             ,
                query['request'] )

    elif query['op'] == 'Predict':
        response = do_predict(
                stub             ,
                query['request'] )

    else:
        print('ERROR: unknown operation')
        return -1

    if args.print:
        print( text_format.MessageToString(response, descriptor_pool = pool) )

    if args.json_output:
        with open(args.json_output, 'w') as json_outfile:
            response_json = json_format.MessageToDict(response, descriptor_pool=pool)
            json.dump(response_json, json_outfile, default=str, indent=2)

    if args.text_output:
        with open(args.text_output, 'w') as text_outfile:
            text_format.PrintMessage(response, text_outfile, indent=2, descriptor_pool=pool)


if __name__ == '__main__':
    main()