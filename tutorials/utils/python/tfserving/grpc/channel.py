import grpc

def get_grpc_channel(
        server: str
):
    return grpc.insecure_channel(server)