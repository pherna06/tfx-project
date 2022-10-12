import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Prediction API #
from tensorflow_serving.apis import classification_pb2
from tensorflow_serving.apis import get_model_metadata_pb2
from tensorflow_serving.apis import inference_pb2
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import regression_pb2

# Model API #
from tensorflow_serving.apis import get_model_status_pb2
from tensorflow_serving.apis import model_management_pb2

# Protobuf #
from google.protobuf import json_format
from google.protobuf import text_format
from google.protobuf import descriptor_pool

### TensorFlow Serving Protobuf Messsages ###

_PROTOBUF_MESSAGES = {
    # Requests #
    # Prediction API
    'PredictRequest': predict_pb2.PredictRequest,
    'ClassificationRequest': classification_pb2.ClassificationRequest,
    'RegressionRequest': regression_pb2.RegressionRequest,
    'MultiInferenceRequest': inference_pb2.MultiInferenceRequest,
    'GetModelMetadataRequest': get_model_metadata_pb2.GetModelMetadataRequest,
    
    # Model API
    'GetModelStatusRequest': get_model_status_pb2.GetModelStatusRequest,
    'ReloadConfigRequest': model_management_pb2.ReloadConfigRequest,

    # Responses #
    # Prediction API
    'PredictResponse': predict_pb2.PredictResponse,
    'ClassificationResponse': classification_pb2.ClassificationResponse,
    'RegressionResponse': regression_pb2.RegressionResponse,
    'MultiInferenceResponse': inference_pb2.MultiInferenceResponse,
    'GetModelMetadataResponse': get_model_metadata_pb2.GetModelMetadataResponse,

    # Model API
    'GetModelStatusResponse': get_model_status_pb2.GetModelStatusResponse,
    'ReloadConfigResponse': model_management_pb2.ReloadConfigResponse
}

def get_message_types():
    return list(_PROTOBUF_MESSAGES.keys())

_PROTOBUF_DESCRIPTORS = {
    'SignatureDefMap': get_model_metadata_pb2.SignatureDefMap.DESCRIPTOR
}

def get_descriptor_types():
    return list(_PROTOBUF_DESCRIPTORS.keys())

def message_from_json(
        message_json: dict,
        message_type: str
):
    Message = _PROTOBUF_MESSAGES.get(message_type)
    if Message:
        return json_format.ParseDict(message_json, Message())
    else:
        print(f"ERROR: unkwown message type: {message_type}")
        return None

def message_to_json(
        message,
        parse_args: dict = {},
        descriptors: list = []
):
    if not parse_args:
        # default
        parse_args['indent'] = 2

    if descriptors:
        pool = descriptor_pool.Default()
        for item in descriptors:
            pool.AddDescriptor( _PROTOBUF_DESCRIPTORS[item] )
        parse_args['descriptor_pool'] = pool

    return json_format.MessageToJson(message, **parse_args)


def message_from_text(
        message_text: str,
        message_type: str
):
    Message = _PROTOBUF_MESSAGES.get(message_type)
    if Message:
        return text_format.Parse(message_text, Message())
    else:
        print(f"ERROR: unkwown message type: {message_type}")
        return None

def message_to_text(
        message,
        parse_args: dict = {},
        descriptors: list = []
):
    if not parse_args:
        # default
        pass

    if descriptors:
        pool = descriptor_pool.Default()
        for item in descriptors:
            pool.AddDescriptor( _PROTOBUF_DESCRIPTORS[item] )
        parse_args['descriptor_pool'] = pool

    return text_format.MessageToString(message, **parse_args)