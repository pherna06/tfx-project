import argparse
import json

import os
_SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(f'{_SCRIPTDIR}/..')

import tfserving

### INFO COMMAND ###

def do_info_messages(
        search_list: list = None
):
    available = tfserving.protobuf.get_message_types()
    if search_list:
        for item in search_list:
            print(f"· {item} ({'AVAILABLE' if item in available else 'UNKNOWN'})")
    else:
        print("Available message types:")
        for msg_type in available:
            print(f"· {msg_type}")

def do_info_formats(
        search_list: list = None
):
    available = tfserving.protobuf.get_message_file_formats()
    if search_list:
        for item in search_list:
            print(f"· {item} ({'AVAILABLE' if item in available else 'UNKNOWN'})")
    else:
        print("Available file formats:")
        for format_type in available:
            print(f"· {format_type}")

_INFO_TYPES = {
    'messages': do_info_messages,
    'formats': do_info_formats
}

def do_command_info(args):
    do_command = _INFO_TYPES.get(args.type)
    if do_command:
        command_args = {}
        if args.search:
            command_args['search_list'] = args.search
        
        do_command(**command_args)
    else:
        print(f"ERROR: unknown info command: {args.type}")

### GEN COMMAND ###

def do_command_gen(args):
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
    desc = ("A command interface to use the local 'tfserving.protobuf' "
            "module for generation of TensorFlow Serving protobuf "
            "messages as files in different protobuf formats.")
    parser = argparse.ArgumentParser(description = desc)
    subparsers = parser.add_subparsers()

    # Consultation subparser.
    info_parser_desc = ("Subcommand used to consult the different "
                        "message and file format types available.")
    info_parser = subparsers.add_parser('info', help = info_parser_desc)

    info_type_help = ("Use 'messages' to consult available messages. "
                      "Use 'formats' to consult available file formats.")
    info_parser.add_argument(
        'type',
        metavar = 'TYPE',
        help = info_type_help,
        type = str)

    info_search_help = ("Additional option to search for specific message "
                        "or format types.")
    info_parser.add_argument(
        '-s', '--search',
        help = info_search_help,
        type = str,
        nargs = '+')

    info_parser.set_defaults(func = do_command_info)

    # Generation subparser
    gen_parser_desc = ("Subcommand used to generate a protobuf message "
                       "and load it in an output file.")
    gen_parser = subparsers.add_parser('gen', help = gen_parser_desc)

    gen_type_help = ("Name of the message type to be generated")
    gen_parser.add_argument(
        'type',
        metavar = 'TYPE',
        help = gen_type_help,
        type = str)

    gen_format_help = ("Optional argument to choose the format for the "
                       "protobuf message file. If not set, user can pick "
                       "the format using terminal input.")
    gen_parser.add_argument(
        '-f', '--format',
        help = gen_format_help,
        type = str)
    
    gen_input_help = ("Optional path to JSON file with dict to fill in the "
                      "specified fields of a message automatically. This dict "
                      "structure does not strictly follow that of protobuf "
                      "json-format. Check source code in case of doubt about "
                      "the specific structure.")
    gen_parser.add_argument(
        '-i', '--input',
        help = gen_input_help,
        type = str)

    gen_output_help = ("Optional path to output file where protobuf message "
                       "will be loaded. It is recommended to include the "
                       "desired extension in the file name (i.e. '.json' for "
                       "json-format or '.txt' in text-format. If not set, user "
                       "can pick the file name using terminal input.")
    gen_parser.add_argument(
        '-o', '--output',
        help = gen_output_help,
        type = str)

    gen_parser.set_defaults(func = do_command_gen)

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()