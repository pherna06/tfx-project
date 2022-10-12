def generate_random_PredictRequest(size):
    args = {}
    args['model_spec'] = {}
    args['model_spec']['name']= 'mnist'
    args['model_spec']['signature_name'] = 'predict_images'

    args['inputs'] = {}
    args['inputs']['images'] = np.random.rand(size, 28 * 28).tolist()

    args['output_filter'] = ['scores']

    message = generate_PredictRequest(args = args)
    return message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'size', metavar='SIZE', type=int )
    parser.add_argument(
        '--out', type=str, default=None )

    args = parser.parse_args()

    message = generate_random_PredictRequest(args.size)
    gen_output_file(message, output_file=args.out)

if __name__ == '__main__':
    import os
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    import sys
    sys.path.append(scriptdir + '/../../../..')

    import tfserving
    from tfserving.grpc.requests.protobuf import gen_output_file
    from tfserving.grpc.requests import generate_PredictRequest

    import numpy as np
    import argparse

    main()
