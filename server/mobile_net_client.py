import requests
import json
import numpy as np
import time
from tensorflow.keras.applications.mobilenet import preprocess_input

_server_url = 'http://esfinge.dacya.ucm.es:5000'

def get_instances(size):
    instances = np.random.rand(size, 224, 224, 3) * 255.0
    instances = preprocess_input(instances)

    return instances.tolist()

def query_serving(serving_uri, instances):
    request_json = {
        'signature_name' : 'serving_default' ,
        'instances'      : instances         }
    
    start = time.time()
    response = requests.post(
        serving_uri,
        json = request_json )
    elapsed_time = (time.time() - start) * 1000
    assert response.ok, response.text

    return response, elapsed_time

def query_server_decision(decision_uri, params):
    response = requests.get(
        decision_uri    ,
        params = params )
    assert response.ok, response.text

    return response

def notify_server_serving(servings_uri, params):
    response = requests.put(
        servings_uri    ,
        params = params )
    assert response.ok, response.text

    return response


def get_servings():
    servings_uri = _server_url + '/servings'
    response = requests.get(servings_uri)
    print(json.dumps(response.json(), indent=4))

def query_serving_by_uri():
    try:
        # Input size, URI and verbose
        size = int(input('> Input test query size: '))
        serving_uri = input('> Input serving query URI: ')
        print_response = input('> Print serving response? (y/n): ') == 'y'

        # Send test query to serving.
        instances = get_instances(size)
        response, elapsed_time = query_serving(serving_uri, instances)
        
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
        # Input size, ID and verbose
        size = int(input('> Input test query size: '))
        id_num = int(input('> Input serving numeric ID: '))
        print_response = input('> Print serving response? (y/n): ') == 'y'

        # Request for serving data.
        servings_uri = _server_url + '/servings'
        request_params = { 'id' : str(id_num) }
        response = requests.get(
            servings_uri            ,
            params = request_params )

        assert response.ok, response.text
        print('> Selected serving:')
        print(json.dumps(response.json(), indent=4))

        # Send test query to serving.
        serving_uri = response.json()['serving_uri']
        instances = get_instances(size)
        response, elapsed_time = query_serving(serving_uri, instances)

        # Notify server of finished query.
        request_params = {
            'id' : id_num          ,
            'finished_queries' : 1 }
        _ = notify_server_serving(servings_uri, request_params)

    except Exception as err:
        print('An error occurred:')
        print(err)
        print('Could not perform acition.')
    
    else:
        print(f'Query elapsed time: {elapsed_time:.3f} ms')
        if (print_response):
            print(json.dumps(response.json(), indent = 4))

def query_serving_by_server_decision():
    try:
        # Input size and verbose
        size = int(input('> Input test query size: '))
        print_response = input('> Print serving response? (y/n): ') == 'y'

        # Request for serving decision.
        decision_uri = _server_url + '/decision'
        request_params = { 'size' : str(size) } # Possible QoS params.
        response = query_server_decision(decision_uri, request_params)

        print('> Selected serving:')
        print(json.dumps(response.json(), indent=4))

        # Send test query to serving.
        serving_uri = response.json()['serving_uri']
        instances = get_instances(size)
        response, elapsed_time = query_serving(serving_uri, instances)

    except Exception as err:
        print('An error occurred:')
        print(err)
        print('Could not perform acition.')
    
    else:
        print(f'Query elapsed time: {elapsed_time:.3f} ms')
        if (print_response):
            print(json.dumps(response.json(), indent = 4))

def test_query_loop():
    try:
        size = int(input('> Input test queries size: '))
        rep = int(input('> Input number of queries: '))

        servings_uri = _server_url + '/servings'
        decision_uri = _server_url + '/decision'
        decision_params = {'size' : str(size)}
        notify_params = {'finished_queries': 1}
        for i in range(rep):
            # Request for serving decision.
            response = query_server_decision(decision_uri, decision_params)
            serving_uri = response.json()['serving_uri']
            id_num = response.json()['id']

            print(f'> Query {i + 1}: Selected serving:')
            print(json.dumps(response.json(), indent=4))

            # Send test query to serving.
            instances = get_instances(size)
            response, elapsed_time = query_serving(serving_uri, instances)

            # Notify server of finished query.
            notify_params['id'] = id_num
            _ = notify_server_serving(servings_uri, notify_params)

            print(f'Query elapsed time: {elapsed_time:.3f} ms')

    except Exception as err:
        print('An error occurred:')
        print(err)
        print('Could not perform acition.')



_menu_actions = {
    '0' : lambda : ''                      ,
    '1' : get_servings                     ,
    '2' : query_serving_by_uri             ,
    '3' : query_serving_by_id              ,
    '4' : query_serving_by_server_decision ,
    '5' : test_query_loop                  }

_menu_prompt = '**********************************************\n' \
               'Client to perform "fashion_mnist"-like queries\n' \
               '----------------------------------------------\n' \
               'OPTIONS MENU:\n'                                  \
               '    1. Explore available servings.\n'             \
               '    2. Make test query to a serving (by URI).\n'  \
               '    3. Make test query to a serving (by ID).\n'   \
               '    4. Make test query (server-decided).\n'       \
               '    5. Test query loop.\n'                        \
               '\n'                                               \
               '    0. QUIT\n'                                    \
               '\n'                                               \
               '> Input option :  '

def client_menu():
    opt = input(_menu_prompt)
    while opt != '0' and opt in _menu_actions:
        _menu_actions[opt]()
        opt = input(_menu_prompt)

def main():
    client_menu()

if __name__ == '__main__':
    main()