def generate_PredictRequest(deep = 1, args = {}):
    from .protobuf import generate_ModelSpec
    from tensorflow import make_tensor_proto

    name = '\'PredictRequest\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.apis import predict_pb2
    message = predict_pb2.PredictRequest()

    # model_spec #
    if 'model_spec' in args:
        print(f'{indent} Field \'model_spec\' will be generated automatically from args.')
        message.model_spec.CopyFrom( generate_ModelSpec(deep + 1, args=args['model_spec']) )
    else:
        answer = input(f'{indent} Add \'model_spec\' (ModelSpec) field? (y/n): ')
        if answer != 'n':
            message.model_spec.CopyFrom( generate_ModelSpec(deep + 1) )

    # inputs #
    if 'inputs' in args:
        print(f'{indent} Field \'inputs\' will be generated automatically from args, using \'make_tensor_proto\'.')
        for key in args['inputs']:
            tensor_proto = make_tensor_proto(args['inputs'][key])
            message.inputs[key].CopyFrom(tensor_proto)
    else:
        answer = input(f'{indent} Add \'inputs\' (map<string, TensorProto>) field? (y/n): ')
        if answer != 'n':
            while True:
                answer = input(f'{indent} Add pair to \'inputs\'? (y/n): ')
                if answer == 'n':
                    break

                key = input(f'{indent} Input key (string): ')
                value_str = input(f'{indent} Input value (TensorProto) as list: ')
                import json
                value = json.loads(value_str)

                message.inputs[key].CopyFrom( make_tensor_proto(value) )

    # output_filter #
    if 'output_filter' in args:
        print(f'{indent} Field \'output_filter\' will be generated automatically from args.')
        for value in args['output_filter']:
            message.output_filter.append(value)
    else:
        answer = input(f'{indent} Add \'output_filter\' (repeated string) field? (y/n): ')
        if answer != 'n':
            while True:
                answer = input(f'{indent} Add value to \'output_filter\'? (y/n): ')
                if answer == 'n':
                    break

                value = input(f'{indent} Input value (string): ')

                message.output_filter.append(value)

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

    from .requests import protobuf
    from protobuf import gen_output_file

    import argparse

    main()