import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow_serving.apis import prediction_service_pb2_grpc

def get_grpc_stub(
        channel
):
    return prediction_service_pb2_grpc.PredictionServiceStub(channel)

_API_REQUESTS = {
    'GetModelMetadata': 'GetModelMetadataRequest',
    'Predict': 'PredictRequest',
    'Classify': 'ClassificationRequest',
    'Regress': 'RegressionRequest',
    'MultiInference': 'MultiInferenceRequest'
}

def get_request_type(
        service: str
):
    return _API_REQUESTS.get(service)

def call_GetModelMetadata(
        stub,
        request
):
    return stub.GetModelMetadata(request)

def call_Predict(
        stub,
        request
):
    return stub.Predict(request)

def call_Classify(
        stub,
        request
):
    return stub.Classify(request)

def call_Regress(
        stub,
        request
):
    return stub.Regress(request)

def call_MultiInference(
        stub,
        request
):
    return stub.MultiInference(request)

_API_SERVICES = {
    'GetModelMetadata': call_GetModelMetadata,
    'Predict': call_Predict,
    'Classify': call_Classify,
    'Regress': call_Regress,
    'MultiInference': call_MultiInference
}

def get_service_types():
    return list(_API_SERVICES.keys())

def get_service(
        service: str
):
    return _API_SERVICES.get(service)