import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow_serving.apis import model_service_pb2_grpc

def get_grpc_stub(
        channel
):
    return model_service_pb2_grpc.ModelServiceStub(channel)

_API_REQUESTS = {
    'GetModelStatus': 'GetModelStatusRequest',
    'HandleReloadConfigRequest': 'ReloadConfigRequest'
}

def get_request_type(
        service: str
):
    return _API_REQUESTS.get(service)

def call_GetModelStatus(
        stub,
        request
):
    return stub.GetModelStatus(request)

def call_HandleReloadConfigRequest(
        stub,
        request
):
    return stub.HandleReloadConfigRequest(request)

_API_SERVICES = {
    'GetModelStatus': call_GetModelStatus,
    'HandleReloadConfigRequest': call_HandleReloadConfigRequest
}

def get_service_types():
    return list(_API_SERVICES.keys())

def get_service(
        service: str
):
    return _API_SERVICES.get(service)