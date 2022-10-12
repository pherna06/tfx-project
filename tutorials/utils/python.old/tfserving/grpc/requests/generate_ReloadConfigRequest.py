def generate_ReloadConfigRequest(deep = 1):
    name = '\'ReloadConfigRequest\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.apis import model_management_pb2
    message = model_management_pb2.ReloadConfigRequest()

    answer = input(f'{indent} Add \'config\' (ModelServerConfig) field? (y/n): ')
    if answer != 'n':
        from protobuf import generate_ModelServerConfig
        message.config.CopyFrom( generate_ModelServerConfig(deep + 1) )

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out', type=str, default=None )

    args = parser.parse_args()

    message = generate_PredictRequest()
    gen_output_file(message, output_file=args.out)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from protobuf import gen_output_file

    import argparse

    main()
