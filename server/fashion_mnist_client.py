import requests

_server_url = 'https://esfinge.dacya.ucm.es:5000'

def get_servings():
    servings_uri = _server_url + '/servings'
    response = requests.get(servings_url)
    print(response.json())

_menu_actions = [
    lambda : 0,
    get_servings
]

_menu_promt = 'Client to perform "fashion_mnist"-like queries\n' \
              '----------------------------------------------\n' \
              'OPTIONS MENU:\n'                                  \
              '    1. Explore available servings.\n'             \
              '\n'                                               \
              '    0. QUIT\n'                                    \
              '\n'                                               \
              '> Input option :  '

def client_menu():
    opt = 0
    while opt in _menu_actions:
        opt = input(_menu_prompt)
        if opt == 0:
            break
        _menu_actions[opt]()

def main():
    client_menu()

if __name__ == '__main__':
    main()