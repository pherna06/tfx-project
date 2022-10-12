def generate_GetModelMetadataRequest(deep = 1):
    name = '\'GetModelMetadataRequest\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.apis import get_model_metadata_pb2
    message = get_model_metadata_pb2.GetModelMetadataRequest()

    answer = input(f'{indent} Add \'model_spec\' (ModelSpec) field? (y/n): ')
    if answer != 'n':
        from protobuf import generate_ModelSpec
        message.model_spec.CopyFrom( generate_ModelSpec(deep + 1) )

    answer = input(f'{indent} Add \'metadata_field\' (repeated string) field? (y/n): ')
    if answer != 'n':
        while True:
            answer = input(f'{indent} Add element to \'metadata_field\'? (y/n): ')
            if answer == 'n':
                break

            value = input(f'{indent} Input value (string): ')
            message.metadata_field.append(value)

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out', type=str, default=None )

    args = parser.parse_args()

    message = generate_GetModelMetadataRequest()
    gen_output_file(message, output_file=args.out)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from protobuf import gen_output_file

    import argparse

    main()
