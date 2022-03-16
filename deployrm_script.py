import yaml
import subprocess

def main():
    with open('./deployment.yml', 'r') as deplo_yaml:
        deployment = yaml.load(deplo_yaml, Loader=yaml.FullLoader)

    cmd = ['docker', 'rm', '-f', '']

    for deploy in deployment:
        model = deploy['model']
        cmd[-1] = model['cont_name']
        subprocess.run(args=cmd)

        prom = deploy['prometheus']
        cmd[-1] = prom['cont_name']
        subprocess.run(args=cmd)

if __name__ == '__main__':
	main()
