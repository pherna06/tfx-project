def generate_ModelConfigList(deep = 1):
    name = '\'ModelConfigList\''
    indent = deep * '>'
    print(f'{indent} Generating', name, 'Message...')
    
    from tensorflow_serving.config import model_server_config_pb2
    message = model_server_config_pb2.ModelConfigList()

    answer = input(f'{indent} Add \'config\' (repeated ModelConfig) field? (y/n): ')
    if answer != 'n':
        from generate_ModelConfig import generate_ModelConfig
        
        while True:
            answer = input(f'{indent} Add element to \'config\'? (y/n): ')
            if answer == 'n':
                break
            
            message.config.append( generate_ModelConfig(deep + 1) )

    print(f'{indent} No more fields left in', name, 'message.')

    return message

def main():
    message = generate_ModelConfigList()
    gen_output_file(message)

if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    from message_output_file import gen_output_file
    main()
