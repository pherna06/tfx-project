def generate_GetModelStatusRequest(deep = 1):
    name = '\'GetModelStatusRequest\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.apis import get_model_status_pb2
    message = get_model_status_pb2.GetModelStatusRequest()

    answer = input(f'{indent} Add \'model_spec\' (ModelSpec) field? (y/n): ')
    if answer != 'n':
        from protobuf import generate_ModelSpec
        message.model_spec.CopyFrom( generate_ModelSpec(deep + 1) )

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
