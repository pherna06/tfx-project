import yaml
from deploy_utils import deploy_serving, deploy_prometheus

def main():
    with open('./deployment.yml', 'r') as deplo_yaml:
        deployment = yaml.load(deplo_yaml)

    for deploy in deployment:
        model = deploy['model']
        deploy_serving(**model)

        prom = deploy['prometheus']
        deploy_prometheus(**prom)

if __name__ == '__main__':
	main()