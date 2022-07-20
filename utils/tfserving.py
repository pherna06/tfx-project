import subprocess
import argparse

def get_parser():
	desc = "A script that runs a TF Serving Docker image with the options"
	desc += " of a configuration file."
	parser = argparse.ArgumentParser(description=desc)

	config_help = "Path to JSON configuration file"
	parser.add_argument(
		'config', metavar='CONFIG', help=config_help,
		type=str, required=True )

	return parser

def main():
	parser = get_parser()
	args = parser.parse_args()

	with open(args.config) as json_file:
		config = json.load(json_file)

	command = ['docker', 'run']
	for opt in config['docker']:
		command.append(opt)

	command.append( config['docker_image'] )

	for opt in config['tensorflow_model_server']:
		command.append(opt)

	subprocess.run(args=command)

if __name__ == '__main__':
	main()