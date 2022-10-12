def generate_ServableVersionPolicy(deep = 1):
    name = '\'ServableVersionPolicy\''
    indent = '>' * deep
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.config import file_system_storage_path_source_pb2
    message = file_system_storage_path_source_pb2.FileSystemStoragePathSourceConfig.ServableVersionPolicy()

    answer = input(f'{indent} Add \'policy_choice\' (oneof) field? (y/n): ')
    if answer != 'n':
        oneof_menu  = "Choose a field:\n"
        oneof_menu += "\t1.latest (Latest)\n"
        oneof_menu += "\t2.all (All)\n"
        oneof_menu += "\t3.specific (Specific)\n"
        oneof_menu += "Choose: "
        answer = int( input(f'{indent} {oneof_menu}') )

        if answer == 1:
            print(f'{indent}> Generating \'Latest\' Message...')

            answer = input(f'{indent}> Add \'num_versions\' (uint32) field (y/n): ')
            if answer != 'n':
                message.latest.num_versions = int( input(f'{indent}> Input \'num_versions\': ') )

            print(f'{indent}> No more fields left in \'Latest\' message.')

        if answer == 2:
            print(f'{indent}> Generating \'All\' Message...')
            message.all.SetInParent()
            print(f'{indent}> No more fields left in \'All\' message.')

        if answer == 3:
            print(f'{indent}> Generating \'Specific\' Message...')

            answer = input(f'{indent}> Add \'versions\' (repeated int64) field (y/n): ')
            if answer != 'n':
                while True:
                    answer = input(f'{indent}> Add element to \'versions\' field? (y/n): ')
                    if answer == 'n':
                        break

                    value = int( input(f'{indent}> Input value (int64): ') )
                    message.specific.versions.append(value)

            print(f'{indent}> No more fields left in \'Specific\' message.')

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    message = generate_ServableVersionPolicy()
    gen_output_file(message)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file
    main()
