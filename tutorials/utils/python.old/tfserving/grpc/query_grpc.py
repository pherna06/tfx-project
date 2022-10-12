import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import argparse
import json

import grpc

from tensorflow_serving.apis import model_service_pb2_grpc
from google.protobuf import json_format, text_format


### MODEL API ###

# GetModelStatus #

def do_get_model_status(
        stub         ,
        request_dict ):

    from tensorflow_serving.apis import get_model_status_pb2

    request = json_format.ParseDict(
            request_dict ,
            get_model_status_pb2.GetModelStatusRequest() )

    # >> Call Service <<
    response = stub.GetModelStatus(request)

    # Print result
    return {'response': response}

# -------------- #

# HandleReloadConfigRequest #

def do_handle_reload_config_request(
        stub         ,
        request_dict ):

    from tensorflow_serving.apis import model_management_pb2

    request = json_format.ParseDict(
            request_dict ,
            model_management_pb2.ReloadConfigRequest() )

    response = stub.HandleReloadConfigRequest(request)

    return {'response': response}

# ------------------------- #

### PREDICTION API ###

# Predict #

def do_predict(
        stub         ,
        request_dict ):
    
    from tensorflow_serving.apis import predict_pb2

    request = json_format.ParseDict(
            request_dict ,
            predict_pb2.PredictRequest() )

    response = stub.Predict(request)

    return {'response': response}

# ------- #

# Classify #

def do_classify(
        stub         ,
        request_dict ):
    pass

# -------- #

# Regress #

def do_regress(
        stub         ,
        request_dict ):
    pass

# ------- #

# MultiInference #

def do_multi_inference(
        stub         ,
        request_dict ):
    pass

# -------------- #

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
    pool.AddDescriptor(get_model_metadata_pb2.SignatureDefMap.DESCRIPTOR)

    return {
        'response' : response ,
        'pool'     : pool     }

# ---------------- #

### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###




def get_parser():
    desc = "A script that runs a query to a TensorFlow Serving gRPC API."
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
    _PREDICTION_API = {
        'Predict'          : do_predict            ,
        'Classify'         : do_classify           ,
        'Regress'          : do_regress            ,
        'MultiInference'   : do_multi_inference    ,
        'GetModelMetadata' : do_get_model_metadata }

    _MODEL_API = {
        'GetModelStatus'            : do_get_model_status             ,
        'HandleReloadConfigRequest' : do_handle_reload_config_request }

    parser = get_parser()
    args = parser.parse_args()

    with open(args.query, 'r') as json_file:
        query = json.load(json_file)

    try:
        # Connect to gRPC server
        assert ('server' in query), (
            'ERROR: introduce the gRPC server in \'server\' key'
        )

        channel = grpc.insecure_channel(query['server'])

    except Exception as e:
        print(e)
        return -1

    
    try:
        # Decide API operation
        assert ('op' in query), (
            'ERROR: introduce the gRPC API operation name in \'op\' key'
        )

        assert( (query['op'] in _PREDICTION_API) or (query['op'] in _MODEL_API) ), (
            'ERROR: unknown gRPC API operation name'
        )

        stub = None
        do_rpc = None
        if query['op'] in _PREDICTION_API:
            from tensorflow_serving.apis import prediction_service_pb2_grpc
            stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
            do_rpc = _PREDICTION_API[query['op']]

        if query['op'] in _MODEL_API:
            from tensorflow_serving.apis import model_service_pb2_grpc
            stub = model_service_pb2_grpc.ModelServiceStub(channel)
            do_rpc = _MODEL_API[query['op']]
    
    except Exception as e:
        print(e)
        channel.close()
        return -1

    try:
        assert ('request' in query), (
            'ERROR: introduce the protobuf request message (json-format) in \'request\' key'
        )

        result = do_rpc(
            stub             ,
            query['request'] )

    except Exception as e:
        print(e)
        channel.close()
        return -1

    # Output gRPC response
    response = result.get('response')
    pool     = result.get('pool')
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
