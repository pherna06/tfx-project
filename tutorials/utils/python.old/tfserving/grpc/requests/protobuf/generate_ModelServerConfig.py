def generate_ModelServerConfig(deep = 1):
    name = '\'ModelServerConfig\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.config import model_server_config_pb2
    message = model_server_config_pb2.ModelServerConfig()

    answer = input(f'{indent} Add \'config\' (oneof) field? (y/n): ')
    if answer != 'n':
        oneof_menu  = "Choose a field:\n"
        oneof_menu += "\t1.model_config_list (ModelConfigList)\n"
        oneof_menu += "\t2.[NOT AVAILABLE] custom_model_config (google.protobuf.Any)\n"
        oneof_menu += "Choose: "
        answer = int( input(f'{indent} {oneof_menu}') )

        if answer == 1:
            from generate_ModelConfigList import generate_ModelConfigList
            message.model_config_list.CopyFrom( generate_ModelConfigList(deep + 1) )

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out', type=str, default=None )

    args = parser.parse_args()

    message = generate_ModelServerConfig()
    gen_output_file(message, output_file=args.out)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file

    import argparse

    main()
