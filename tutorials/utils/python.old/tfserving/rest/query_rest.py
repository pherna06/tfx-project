import argparse
import json

import requests

# Predict #

def do_predict(
        server     ,
        model_spec ,
        inputs     ):

    # URL
    query_url = 'http://'
    query_url += server
    query_url += '/v1/models/'

    if 'name' in model_spec:
        query_url += model_spec['name']
    else:
        print('ERROR: no model name specified')
        return

    if 'version' in model_spec:
        query_url += '/versions/'
        query_url += str(model_spec['version'])

    if 'version_label' in model_spec:
        query_url += '/labels/'
        query_url += model_spec['version_label']

    query_url += ':predict'

    # DATA
    query_data = {}

    if 'signature_name' in model_spec:
        query_data['signature_name'] = model_spec['signature_name']

    query_data['inputs'] = {}
    for alias in inputs:
        query_data['inputs'][alias] = inputs[alias]

    # > QUERY <
    response = requests.post(
        query_url,
        data = json.dumps(query_data) )
    return response.json()

### ### ### ###




# Classify #

def do_classify(
        server        ,
        model_spec    ,
        context       ,
        examples      ):

    # URL
    query_url = 'http://'
    query_url += server
    query_url += '/v1/models/'

    if 'name' in model_spec:
        query_url += model_spec['name']
    else:
        print('ERROR: no model name specified')
        return

    if 'version' in model_spec:
        query_url += '/versions/'
        query_url += str(model_spec['version'])

    if 'version_label' in model_spec:
        query_url += '/labels/'
        query_url += model_spec['version_label']

    query_url += ':classify'

    # DATA
    query_data = {}

    if 'signature_name' in model_spec:
        query_data['signature_name'] = model_spec['signature_name']

    if context:
        query_data['context'] = context

    query_data['examples'] = []
    for example in examples:
        query_data['examples'].append(example)

    # > QUERY <
    response = requests.post(
        query_url,
        data = json.dumps(query_data) )
    return response.json()

### ### ### ###




# Regress #

def do_regress(
        server        ,
        model_spec    ,
        context       ,
        examples      ):

    # URL
    query_url = 'http://'
    query_url += server
    query_url += '/v1/models/'

    if 'name' in model_spec:
        query_url += model_spec['name']
    else:
        print('ERROR: no model name specified')
        return

    if 'version' in model_spec:
        query_url += '/versions/'
        query_url += str(model_spec['version'])

    if 'version_label' in model_spec:
        query_url += '/labels/'
        query_url += model_spec['version_label']

    query_url += ':regress'

    # DATA
    query_data = {}

    if 'signature_name' in model_spec:
        query_data['signature_name'] = model_spec['signature_name']

    if context:
        query_data['context'] = context

    query_data['examples'] = []
    for example in examples:
        query_data['examples'].append(example)

    # > QUERY <
    response = requests.post(
        query_url,
        data = json.dumps(query_data) )
    return response.json()

### ### ### ###



# GetModelMetadata #

def do_get_model_metadata(
        server     ,
        model_spec ):

    query_url = 'http://'
    query_url += server
    query_url += '/v1/models/'

    if 'name' in model_spec:
        query_url += model_spec['name']
    else:
        print('ERROR: no model name specified')
        return

    if 'version' in model_spec:
        query_url += '/versions/'
        query_url += str(model_spec['version'])

    if 'version_label' in model_spec:
        query_url += '/labels/'
        query_url += model_spec['version_label']

    query_url += '/metadata'

    response = requests.get(query_url)
    return response.json()

### ### ### ###

### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ###




def get_parser():
    desc = "A script that runs a gRPC query to a TensorFlow serving."
    desc += " This is an example script, which implements functionality "
    desc += " ONLY for float data types."
    parser = argparse.ArgumentParser(description=desc)

    query_help = "Path to JSON query file"
    parser.add_argument(
            'query', metavar='QUERY', help=query_help,
            type=str )

    output_help = "Path to JSON query result file"
    parser.add_argument(
            '-o', '--output', metavar='output', help=output_help,
            type=str, default=None )

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    with open(args.query) as json_file:
        query = json.load(json_file)

    # gRPC server
    if 'server' not in query:
        print('ERROR: gRPC server not specified')
        return -1

    stub = None

    # Op parsing
    if 'op' not in query:
        print('ERROR: operation not specified.')
        return -1

    if   query['op'] == 'Predict':
        result = do_predict(
                query['server']        ,
                query['model_spec']    ,
                query['inputs']        )

    elif query['op'] == 'Classify':
        result = do_classify(
                query['server']     ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'Regress':
        result = do_regress(
                query['server']     ,
                query['model_spec'] ,
                query['context']    ,
                query['examples']   )

    elif query['op'] == 'GetModelMetadata':
        result = do_get_model_metadata(
                query['server']         ,
                query['model_spec']     )

    else:
        print('ERROR: unknown operation')
        return -1

    if args.output:
        with open(args.output, 'w') as outjson:
            json.dump(result, outjson, default=str, indent=4)
    else:
        print(result)


if __name__ == '__main__':
    main()
