from google.protobuf import text_format
from google.protobuf import json_format
import json

def gen_text_file(
        message,
        out_file: str = None
):
    if out_file:
        name = out_file
    else:
        name = input("Input name for output text file: ")

    print(f"Saving text-format protobuf in {name}")
    with open(name, 'w') as text_file:
        text_format.PrintMessage(message, text_file)

def gen_json_file(
        json_dict: dict,
        out_file: str = None
):
    if out_file:
        name = out_file
    else:
        name = input("Input name for output JSON file: ")

    print(f"Saving json-format protobuf in {name}")
    with open(name, 'w') as json_file:
        json.dump(json_dict, json_file, indent=2)


_MESSAGE_FILE_FORMATS = [
    'text',
    'json'
]

def get_message_file_formats():
    return _MESSAGE_FILE_FORMATS

def gen_output_file(
        message,
        out_format: str = None,
        out_file: str = None
):
    if out_format not in _MESSAGE_FILE_FORMATS:
        output_menu = ("Available output formats:\n"
                       "  0. Do nothing (message will be discarded!)\n"
                       "  1. text-format\n"
                       "  2. json-format\n"
                       "Choose format: ")
        answer = int( input(output_menu) )
    elif out_format == 'text':
        answer = 1
    elif out_format == 'json':
        answer = 2

    # text-format
    if answer == 1:
        print("> text-format chosen.")

        gen_text_file(message, out_file)

    # json-format
    if answer == 2:
        print("> json-format chosen.")

        answer = input("Add customized pairs to JSON? (Yes: any | No 'n'): ")
        if answer != 'n':
            output_dict = {}

            message_key = input("Set key string for message: ")
            output_dict[message_key] = json_format.MessageToDict(message)

            answer = input("Add another key-value pair? (Yes: any | No 'n'): ")
            while answer != 'n':
                key = input("Set key: ")
                value_str = input("Set value: ")
                value = json.loads( value_str )

                output_dict[key] = value

                answer = input("Add another key-value pair? (Yes: any | No 'n'): ")
        else:
            output_dict = json_format.MessageToDict(message)

        gen_json_file(output_dict, out_file)