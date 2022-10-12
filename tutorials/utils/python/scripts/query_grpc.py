import argparse
import json

import os
_SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(f'{_SCRIPTDIR}/..')

import tfserving

### INFO COMMAND ###

def do_command_info_protobuf(args):
    messages = tfserving.grpc.messages.get_message_types()
    descriptors = tfserving.grpc.messages.get_descriptor_types()
    if args.search:
        for item in args.search:
            if item in messages:
                print(f"· {item} (MESSAGE)")
            elif item in descriptors:
                print(f"· {item} (DESCRIPTOR)")
            else:
                print(f"· {item} (UNKNOWN)")
    else:
        print("Available Protobuf messages:")
        for msg_type in messages:
            print(f"· {msg_type}")
        print("Available Protobuf descriptors:")
        for desc_type in descriptors:
            print(f"· {desc_type}")

def do_command_info_model(args):
    available = tfserving.grpc.model_api.get_service_types()
    if args.search:
        for item in args.search:
            if item in available:
                request = tfserving.grpc.model_api.get_request_type(item)
                print(f"· {item} [{request}] (AVAILABLE)")
            else:
                print(f"· {item} (UNKNOWN)")
    else:
        print("Available GRPC services:")
        for service in available:
            request = tfserving.grpc.model_api.get_request_type(service)
            print(f"· {service} [{request}]")

def do_command_info_prediction(args):
    available = tfserving.grpc.prediction_api.get_service_types()
    if args.search:
        for item in args.search:
            if item in available:
                request = tfserving.grpc.prediction_api.get_request_type(item)
                print(f"· {item} [{request}] (AVAILABLE)")
            else:
                print(f"· {item} (UNKNOWN)")
    else:
        print("Available GRPC services:")
        for service in available:
            request = tfserving.grpc.prediction_api.get_request_type(service)
            print(f"· {service} [{request}]")

### QUERY COMMAND ###

def get_request_from_input(request_type, args):
    if args.in_json:
        with open(args.in_json, 'r') as in_json_file:
            in_dict = json.load(in_json_file)
        request = tfserving.grpc.messages.message_from_json(in_dict, request_type)
    if args.in_text:
        with open(args.in_text, 'r') as in_text_file:
            in_text = in_text_file.read()
        request = tfserving.grpc.messages.message_from_text(in_text, request_type)

    return request

def handle_response_output(response, args):
    message_text = None
    if args.print:
        message_text = tfserving.grpc.messages.message_to_text(
            response,
            descriptors = args.descriptors)
        print(message_text)
    if args.out_json:
        message_json = tfserving.grpc.messages.message_to_json(
            response,
            descriptors = args.descriptors)
        with open(args.out_json, 'w') as out_json_file:
            out_json_file.write(message_json)
    if args.out_text:
        if not message_text:
            message_text = tfserving.grpc.messages.message_to_text(
                response,
                descriptors = args.descriptors)
        with open(args.out_text, 'w') as out_text_file:
            out_text_file.write(message_text)


def do_command_query_model(args):
    Service = tfserving.grpc.model_api.get_service(args.service)
    if Service:
        # Input request
        request_type = tfserving.grpc.model_api.get_request_type(args.service)
        request = get_request_from_input(request_type, args)

        # Open GRPC channel
        channel = tfserving.grpc.channel.get_grpc_channel(args.server)
        stub = tfserving.grpc.model_api.get_grpc_stub(channel)

        # Query Service
        response = Service(stub, request)

        # Output response
        handle_response_output(response, args)
    else:
        print(f"ERROR: unknown Model API service: {args.service}")

def do_command_query_prediction(args):
    Service = tfserving.grpc.prediction_api.get_service(args.service)
    if Service:
        # Input request
        request_type = tfserving.grpc.prediction_api.get_request_type(args.service)
        request = get_request_from_input(request_type, args)
        
        # Open GRPC channel
        channel = tfserving.grpc.channel.get_grpc_channel(args.server)
        stub = tfserving.grpc.prediction_api.get_grpc_stub(channel)

        # Query Service
        response = Service(stub, request)

        # Output response
        handle_response_output(response, args)
    else:
        print(f"ERROR: unknown Prediction API service: {args.service}")

### MODEL COMMAND ###

def do_command_model(args):
    gen_args = {}
    gen_args['msg'] = args.type
    if args.format:
        gen_args['out_format'] = args.format
    if args.output:
        gen_args['out_file'] = args.output
    if args.input:
        with open(args.input, 'r') as input_file:
            message_args = json.load(input_file)
        gen_args['args'] = message_args
    
    tfserving.protobuf.generate_message_file(**gen_args)

### PARSER ###

def get_parser():
    # Parser description and creation
    desc = ("A command interface to use the local 'tfserving.grpc' "
            "module for using GRPC APIs of a TensorFlow serving.")
    parser = argparse.ArgumentParser(description = desc)
    subparsers = parser.add_subparsers()

    # INFO COMMAND #
    info_parser_desc = ("Subcommand used to consult the different "
                        "GRPC APIs services available.")
    info_parser = subparsers.add_parser('info', help = info_parser_desc)
    info_subparsers = info_parser.add_subparsers()

    def setup_info_parser(this_parser):
        info_search_help = ("Additional option to search for specific services.")
        this_parser.add_argument(
            '-s', '--search',
            help = info_search_help,
            type = str,
            nargs = '+')

    # Protobuf
    info_protobuf_parser_desc = ("Subcommand used to consult the different "
                                 "protobuf message types and descriptors "
                                 "available.")
    info_protobuf_parser = info_subparsers.add_parser('protobuf', help = info_protobuf_parser_desc)

    setup_info_parser(info_protobuf_parser)

    info_protobuf_parser.set_defaults(func = do_command_info_protobuf)

    # Model
    info_model_parser_desc = ("Subcommand used to consult the different "
                              "GRPC Model API services available.")
    info_model_parser = info_subparsers.add_parser('model', help = info_model_parser_desc)

    setup_info_parser(info_model_parser)

    info_model_parser.set_defaults(func = do_command_info_model)

    # Prediction
    info_prediction_parser_desc = ("Subcommand used to consult the different "
                                   "GRPC Prediction API services available.")
    info_prediction_parser = info_subparsers.add_parser('prediction', help = info_prediction_parser_desc)

    setup_info_parser(info_prediction_parser)

    info_prediction_parser.set_defaults(func = do_command_info_prediction)


    # QUERY COMMAND #
    query_parser_desc = ("Subcommand used to query the different GRPC APIs "
                         "services of a serving")
    query_parser = subparsers.add_parser('query', help = query_parser_desc)
    query_subparsers = query_parser.add_subparsers()

    def setup_query_parser(this_parser):
        query_server_help = ("Optional argument to set the GRPC server address. "
                    "If not set, 'localhost:8500' is used by default.")
        this_parser.add_argument(
            '-s', '--server',
            help = query_server_help,
            type = str,
            default = 'localhost:8500')

        query_input_group = this_parser.add_mutually_exclusive_group(
                required = True)

        query_input_json_help = ("Path to file with the protobuf request message "
                        "in protobuf json-format.")
        query_input_group.add_argument(
            '--in_json',
            help = query_input_json_help,
            type = str)

        query_input_text_help = ("Path to file with the protobuf request message "
                        "in protobuf text-format.")
        query_input_group.add_argument(
            '--in_text',
            help = query_input_text_help,
            type = str)

        query_descriptors_help = ("Optional argument to provide a list of descriptors "
                                "to parse google.protobuf.Any messages")
        this_parser.add_argument(
            '-d', '--descriptors',
            help = query_descriptors_help,
            type = str,
            nargs = '*')

        query_output_json_help = ("Path to file where the GRPC query protobuf "
                            "response message will be saved, in json-format.")
        this_parser.add_argument(
            '--out_json',
            help = query_output_json_help,
            type = str)

        query_output_text_help = ("Path to file where the GRPC query protobuf "
                            "response message will be saved, in text-format.")
        this_parser.add_argument(
            '--out_text',
            help = query_output_text_help,
            type = str)

        query_print_help = ("Optional flag to print the GRPC query protobuf response "
                    "to stdout.")
        this_parser.add_argument(
            '-p', '--print',
            help = query_print_help,
            action = 'store_true')

    # Model
    query_model_parser_desc = ("Subcommand used to query the different "
                               "GRPC Model API services of a serving.")
    query_model_parser = query_subparsers.add_parser('model', help = query_model_parser_desc)

    query_model_service_help = ("Name of the Model API service to query")
    query_model_parser.add_argument(
        'service',
        metavar = 'SERVICE',
        help = query_model_service_help,
        type = str)

    setup_query_parser(query_model_parser)

    query_model_parser.set_defaults(func = do_command_query_model)

    # Prediction
    query_prediction_parser_desc = ("Subcommand used to query the different "
                                    "GRPC Prediction API services of a serving.")
    query_prediction_parser = query_subparsers.add_parser('prediction', help = query_prediction_parser_desc)

    query_prediction_service_help = ("Name of the Prediction API service to query")
    query_prediction_parser.add_argument(
        'service',
        metavar = 'SERVICE',
        help = query_prediction_service_help,
        type = str)

    setup_query_parser(query_prediction_parser)

    query_prediction_parser.set_defaults(func = do_command_query_prediction)

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()