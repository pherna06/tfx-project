def generate_ModelSpec(deep = 1, args = {}):
    name = '\'ModelSpec\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.apis import model_pb2
    message = model_pb2.ModelSpec()

    # name #
    if 'name' in args:
        print(f'{indent} Field \'name\' will be generated automatically from args.')
        message.name = args['name']
    else:
        answer = input(f'{indent} Add \'name\' (string) field? (y/n): ')
        if answer != 'n':
            message.name = input(f'{indent} Input \'name\': ')

    # version_choice #
    if 'version_choice' in args:
        print(f'{indent} Field \'version_choice\' will be generated automatically from args.')
        if 'version' in args['version_choice']:
            message.version.value = args['version_choice']['version']
        if 'version_label' in args['version_choice']:
            message.version_label = args['version_choice']['version_label']
    else:
        answer = input(f'{indent} Add \'version_choice\' (oneof) field? (y/n): ')
        if answer != 'n':
            oneof_menu  = "Choose a field:\n"
            oneof_menu += "\t1.version (google.protobufInt64Value)\n"
            oneof_menu += "\t2.version_label (string)\n"
            oneof_menu += "Choose: "
            answer = int( input(f'{indent} {oneof_menu}') )

            if answer == 1:
                print(f'{indent}> Generating \'google.protobuf.Int64Value\' Message...')
                
                answer = input(f'{indent}> Add \'value\' (int) field? (y/n): ')
                if answer != 'n':
                    message.version.value = int( input(f'{indent}> Input \'value\': ') )

                print(f'{indent}> No more fields left in \'google.protobuf.Int64Value\' message.')

            if answer == 2:
                message.version_label = input(f'{indent} Input \'version_label\': ')

    # signature_name #
    if 'signature_name' in args:
        print(f'{indent} Field \'model_spec\' will be generated automatically from args.')
        message.signature_name = args['signature_name']
    else:
        answer = input(f'{indent} Add \'signature_name\' (string) field? (y/n): ')
        if answer != 'n':
            message.signature_name = input(f'{indent} Input \'signature_name\': ')

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    message = generate_ModelSpec()
    gen_output_file(message)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file
    main()
