from flask import Flask, request, jsonify

app = Flask(__name__)

def import_servings_from_deployment_config(config_path):
    with open(config_path, 'r') as deploy_yaml:
        deployment = yaml.load(deploy_yaml, Loader=yaml.FullLoader)

    servings = {}
    for i, deploy in enumerate(deployment):
        servings[i] = {}
        servings[i]['id'] = i
        servings[i]['cont_name'] = deplot['model']['cont_name']
        servings[i]['query_uri'] = deploy['model']['query_uri']

    return servings

_servings = import_servings_from_deployment_config('../deploy/deployment.yaml')

@app.get('/servings')
def get_servings():
    return jsonify(servings)

