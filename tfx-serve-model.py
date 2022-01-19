import subprocess
import argparse

CONT_NAME = "fashion_mnist_model"

HOST_MODEL_DIR = "/tmp/models/fashion_mnist"
CONT_MODEL_DIR = "/models/fashion_mnist"

TENSORBOARD = False
HOST_TB_DIR = "/tmp/tensorboard"
CONT_TB_DIR = "/tmp/tensorboard"

def get_parser():
	# Parser description and creation.
	desc = "A command interface that sets the parameters for a model to be"
	desc += " deployed in a Docker container ran with a TensorFlow Serving"
	desc += " image."
	parser = argparse.ArgumentParser(description = desc)

	# Parser argument to set model host dir.
	name_help = "Name for the container."
	parser.add_argument(
		'-n', '--name', metavar='name', help=name_help,
		type=str,
		default=CONT_NAME
	)

	# Parser argument to set model host dir.
	dir_help = "Path to host directory where the trained model is saved."
	parser.add_argument(
		'-d', '--dir', metavar='dir', help=dir_help,
		type=str,
		default=HOST_MODEL_DIR
	)

	# Parser argument to set model host dir.
	cont_dir_help = "Path to container directory for the trained model."
	parser.add_argument(
		'--cont-dir', metavar='cont_dir', help=cont_dir_help,
		type=str,
		default=CONT_MODEL_DIR
	)

	# Parser argument to set tensorboard.
	tb_help = "Expose port 8500 and mount bind image for tensorboard use."
	parser.add_argument(
		'--tensorboard', dest='tensorboard', help=tb_help,
		action='store_true'
	)

	# Parser argument to set model host dir.
	tbdir_help = "Path to host directory for tensorboard."
	parser.add_argument(
		'--tb-dir', metavar='tb_dir', help=tbdir_help,
		type=str,
		default=HOST_TB_DIR
	)

	# Parser argument to set model host dir.
	cont_tbdir_help = "Path to container directory for tensorboard."
	parser.add_argument(
		'--cont-tb-dir', metavar='cont_tb_dir', help=cont_tbdir_help,
		type=str,
		default=CONT_TB_DIR
	)

	return parser

def main():
	parser = get_parser()
	args = parser.parse_args()

	command = []
	command.append('docker')
	command.append('run')
	command.append('--name')
	command.append(f'{args.name}')
	command.append('-p')
	command.append('8501:8501')
	command.append('-v')
	command.append(f'{args.dir}:{args.cont_dir}')
	command.append('-e')
	command.append('MODEL_NAME=fashion_mnist')

	if args.tensorboard:
		command.append('-p')
		command.append('8500:8500')
		command.append('-v')
		command.append(f'{args.tb_dir}:{args.cont_tb_dir}')

	command.append('-itd')
	command.append('tensorflow/serving')

	subprocess.run(args=command)

if __name__ == '__main__':
	main()