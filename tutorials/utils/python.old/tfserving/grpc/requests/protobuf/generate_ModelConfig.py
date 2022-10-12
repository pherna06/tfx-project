def generate_ModelConfig(deep = 1):
    name = '\'ModelConfig\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.config import model_server_config_pb2
    message = model_server_config_pb2.ModelConfig()

    answer = input(f'{indent} Add \'name\' (string) field? (y/n): ')
    if answer != 'n':
        message.name = input(f'{indent} Input \'name\': ')

    answer = input(f'{indent} Add \'base_path\' (string) field? (y/n): ')
    if answer != 'n':
        message.base_path = input(f'{indent} Input \'base_path\': ')

    answer = input(f'{indent} Add \'model_platform\' (string) field? (y/n): ')
    if answer != 'n':
        message.model_platform = input(f'{indent} Input \'model_platform\' (e.g. \'tensorflow\'): ')

    answer = input(f'{indent} Add \'model_version_policy\' (ServableVersionPolicy) field? (y/n): ')
    if answer != 'n':
        from generate_ServableVersionPolicy import generate_ServableVersionPolicy
        message.model_version_policy.CopyFrom( generate_ServableVersionPolicy(deep + 1) )

    answer = input(f'{indent} Add \'version_labels\' (map<string, int64>) field? (y/n): ')
    if answer != 'n':
        while True:
            answer = input(f'{indent} Add a pair to \'version_labels\'? (y/n): ')
            if answer == 'n':
                break

            key = input(f'{indent} Input key (string): ')
            value = int( input(f'{indent} Input value (int64): ') )
            message.version_labels[key] = value

    answer = input(f'{indent} Add \'logging_config\' (LoggingConfig) field? (y/n): ')
    if answer != 'n':
        from generate_LoggingConfig import generate_LoggingConfig
        message.logging_config.CopyFrom( generate_LoggingConfig(deep + 1) )

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    message = generate_ModelConfig()
    gen_output_file(message)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file
    main()
