import requests
import json
import numpy as np
import time

_server_url = 'http://esfinge.dacya.ucm.es:5000'

def get_servings():
    servings_uri = _server_url + '/servings'
    response = requests.get(servings_uri)
    print(json.dumps(response.json(), indent=4))

def query_serving():
    size = int(input('> Input test query size: '))
    serving_uri = input('> Input serving query URI: ')
    print_response = input('> Print response? (y/n): ') == 'y'

    try:
        instances = np.random.rand(size, 28, 28, 1)
        request_json = {
            'signature_name' : 'serving_default' ,
            'instances'      : np.random.rand(size, 28, 28, 1)
        }

        start = time.time()
        response = requests.post(
            serving_uri,
            json = request_json )
        elapsed_time = (time.time() - start) * 1000
    
    except Exception as err:
        print('An error occurred:')
        print(err)
        print('Could not perform action.')
        return

    else:
        print(f'Query elapsed time: {elapsed_time:.3f} ms')
        if (print_response):
            print(json.dumps(response.json(), indent=4))

_menu_actions = [
    lambda : 0    ,
    get_servings  ,
    query_serving ]

_menu_prompt = 'Client to perform "fashion_mnist"-like queries\n' \
              '----------------------------------------------\n' \
              'OPTIONS MENU:\n'                                  \
              '    1. Explore available servings.\n'             \
              '    2. Make test query to a serving.\n'           \
              '\n'                                               \
              '    0. QUIT\n'                                    \
              '\n'                                               \
              '> Input option :  '

def client_menu():
    opt = int(input(_menu_prompt))
    while opt != 0 and opt in range(len(_menu_actions)):
        _menu_actions[opt]()
        opt = int(input(_menu_prompt))

def main():
    client_menu()

if __name__ == '__main__':
    main()