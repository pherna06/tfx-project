def generate_LoggingConfig(deep = 1):
    name = '\'LoggingConfig\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')

    from tensorflow_serving.config import logging_config_pb2
    message = logging_config_pb2.LoggingConfig()

    answer = input(f'{indent} Add \'log_collector_config\' (LogCollectorConfig) field? (y/n): ')
    if answer != 'n':
        from generate_LogCollectorConfig import generate_LogCollectorConfig
        message.log_collector_config.CopyFrom( generate_LogCollectorConfig(deep + 1) )

    answer = input(f'{indent} Add \'sampling_config\' (SamplingConfig) field? (y/n): ')
    if answer != 'n':
        print(f'{indent}> Generating \'SamplingConfig\' message')
        message.sampling_config.SetInParent()

        answer = input(f'{indent}> Add \'sampling_rate\' (double) field? (y/n): ')
        if answer != 'n':
            message.sampling_config.sampling_rate = double( input(f'{indent} Input \'sampling_rate\' (range: [0, 1.0]): ') )

        print(f'{indent}> No more fields left in \'SamplingConfig\' message')

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    message = generate_LoggingConfig()
    gen_output_file(message)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file
    main()
