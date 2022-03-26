import yaml
from flask import Flask, request, jsonify

app = Flask(__name__)

def import_servings_from_deployment_config(config_path):
    with open(config_path, 'r') as deploy_yaml:
        deployment = yaml.load(deploy_yaml, Loader=yaml.FullLoader)

    servings = {}
    for i, deploy in enumerate(deployment):
        servings[i] = {}
        servings[i]['id'] = i
        servings[i]['cont_name'] = deploy['model']['cont_name']
        servings[i]['serving_uri'] = deploy['utils']['serving_uri']

    return servings

_servings = import_servings_from_deployment_config(
    'homelocal/pherna06/repos/tfx-project/deploy/deployment.yml')

@app.get('/servings')
def get_servings():
    args = request.args
    if 'id' in args:
        id_num = int(args['id'])
        if id_num in _servings:
            return jsonify(_servings[id_num])
        else:
            return f'Serving with ID {id_num} not found.', 400
    else:
        return jsonify(_servings)