def generate_LogCollectorConfig(deep = 1):
    name = '\'LogCollectorConfig\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')

    # TODO

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
