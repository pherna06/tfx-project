import requests
import json
import numpy as np
import time

_server_url = 'http://esfinge.dacya.ucm.es:5000'

def get_servings():
    servings_uri = _server_url + '/servings'
    response = requests.get(servings_uri)
    print(json.dumps(response.json(), indent=4))

def query_serving_by_uri():
    try:
        size = int(input('> Input test query size: '))
        serving_uri = input('> Input serving query URI: ')
        print_response = input('> Print serving response? (y/n): ') == 'y'

        instances = np.random.rand(size, 28, 28, 1).tolist()
        request_json = {
            'signature_name' : 'serving_default' ,
            'instances'      : instances         }

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
            print(json.dumps(response.json(), indent = 4))

def query_serving_by_id():
    try:
        size = int(input('> Input test query size: '))
        id_num = int(input('> Input serving numeric ID: '))
        print_response = input('> Print serving response? (y/n): ') == 'y'

        servings_uri = _server_url + '/servings'
        request_params = { 'id' : str(id_num) }
        response = requests.get(
            servings_uri            ,
            params = request_params )

        assert response.ok, response.text
        print('> Selected serving:')
        print(json.dumps(response.json(), indent=4))

        serving_uri = response.json()['serving_uri']
        instances = np.random.rand(size, 28, 28, 1).tolist()
        request_json = {
            'signature_name' : 'serving_default' ,
            'instances'      : instances         }
        
        start = time.time()
        response = requests.post(
            serving_uri,
            json = request_json )
        elapsed_time = (time.time() - start) * 1000

    except Exception as err:
        print('An error occurred:')
        print(err)
        print('Could not perform acition.')
    
    else:
        print(f'Query elapsed time: {elapsed_time:.3f} ms')
        if (print_response):
            print(json.dumps(response.json(), indent = 4))
        

_menu_actions = [
    lambda : ''          ,
    get_servings         ,
    query_serving_by_uri ,
    query_serving_by_id  ]

_menu_prompt = '**********************************************\n' \
               'Client to perform "fashion_mnist"-like queries\n' \
               '----------------------------------------------\n' \
               'OPTIONS MENU:\n'                                  \
               '    1. Explore available servings.\n'             \
               '    2. Make test query to a serving (by URI).\n'  \
               '    3. Make test query to a serving (by ID).\n'   \
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