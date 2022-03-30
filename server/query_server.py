import yaml
import random
import argparse
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
        servings[i]['finished_queries'] = 0

    return servings

parser = argparse.ArgumentParser()
parser.add_argument(
    'config_file', metavar = 'FILE', type=str,
    help='Path to deployment configuration file.'
)
args = parser.parse_args()

_servings = import_servings_from_deployment_config(args.config_file)




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

@app.put('/servings')
def update_servings():
    args = request.args
    if 'id' not in args:
        return f'"id" param needed to update serving data', 400
    id_num = int(args['id'])

    if 'finished_queries' in args:
        _servings[id_num]['finished_queries'] += int(args['finished_queries'])

    return ''

@app.get('/decision')
def decide_serving():
    args = request.args
    if 'size' not in args:
        return f'"size" param needed to decide', 400
    
    size = int(args['size'])
    serving = random.choice(_servings)
    return jsonify(serving)