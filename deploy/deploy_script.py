import argparse
import yaml
from deploy_utils import deploy_serving, deploy_prometheus

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_file', metavar = 'FILE', type=str,
        help='Path to deployment configuration file.'
    )
    args = parser.parse_args()

    with open(args.config_file, 'r') as deplo_yaml:
        deployment = yaml.load(deplo_yaml, Loader=yaml.FullLoader)

    for deploy in deployment:
        model = deploy['model']
        deploy_serving(**model)

        prom = deploy['prometheus']
        deploy_prometheus(**prom)

if __name__ == '__main__':
	main()
