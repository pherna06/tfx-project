import requests

_server_url = 'http://esfinge.dacya.ucm.es:5000'

def get_servings():
    servings_uri = _server_url + '/servings'
    response = requests.get(servings_uri)
    print(response.json())

_menu_actions = [
    lambda : 0,
    get_servings
]

_menu_prompt = 'Client to perform "fashion_mnist"-like queries\n' \
              '----------------------------------------------\n' \
              'OPTIONS MENU:\n'                                  \
              '    1. Explore available servings.\n'             \
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