import subprocess
import argparse

CONT_NAME = "fashion_mnist_model"

HOST_MODEL_DIR = "/tmp/models/fashion_mnist"
CONT_MODEL_DIR = "/models/fashion_mnist"

TENSORBOARD = False
HOST_TB_DIR = "/tmp/tensorboard"
CONT_TB_DIR = "/tmp/tensorboard"

OMP_NUM_THREADS = 16

def get_parser():
	# Parser description and creation.
	desc = "A command interface that sets the parameters for a model to be"
	desc += " deployed in a Docker container ran with a TensorFlow Serving"
	desc += " image."
	parser = argparse.ArgumentParser(description = desc)

	# TFServing image name to deploy.
	image_help = "image:tag of TF Serving image to deploy"
	parser.add_argument(
			'IMAGE', help=image_help,
			type=str
	)

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
		'--model-dir', metavar='model_dir', help=dir_help,
		type=str,
		default=HOST_MODEL_DIR
	)

	# Parser argument to set model container dir.
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

	# Parser argument to set tensorboard host dir.
	tbdir_help = "Path to host directory for tensorboard."
	parser.add_argument(
		'--tb-dir', metavar='tb_dir', help=tbdir_help,
		type=str,
		default=HOST_TB_DIR
	)

	# Parser argument to set tensorboard container dir.
	cont_tbdir_help = "Path to container directory for tensorboard."
	parser.add_argument(
		'--cont-tb-dir', metavar='cont_tb_dir', help=cont_tbdir_help,
		type=str,
		default=CONT_TB_DIR
	)

	# Parser group for parallelism.
	threads = parser.add_mutually_exclusive_group()
	
	# Parser argument for session parallelism (applies to both intra-inter ops)
	session_threads_help = "Number of threads available for TensorFlow Session. "
	session_threads_help += "If not set or set to 0, threads will be autoconfigured."
	threads.add_argument(
			'--session-threads', metavar='session_threads', help=session_threads_help,
			type=int
	)

	# Parser argument for intra and inter ops parallelism
	intra_inter_help = "Number of threads available for intra and inter ops, respectively."
	intra_inter_help += "If not set or set to 0, threads will be autoconfigured."
	threads.add_argument(
			'--intra-inter-threads', metavar='intra_inter_threads', help=intra_inter_help,
			type=int,
			nargs=2
	)

	# Parser argument to set OMP threads.
	omp_threads_help = "Set number of physical cores for OpenMP."
	parser.add_argument(
		'--omp-threads', metavar='omp_threads', help=omp_threads_help,
		type=int,
		default=OMP_NUM_THREADS
	)

	# Parser argument to enable OMP verbosity.
	omp_verbose_help = "Enable OMP verbosity in container terminal."
	parser.add_argument(
		'--omp-verbose', dest='omp_verbose', help=omp_verbose_help,
		action='store_true'
	)


	# Parser argument to run container detached.
	detached_help = "Run container detached."
	parser.add_argument(
			'-d', '--detached', dest='detached', help=detached_help,
			action='store_true'
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
	command.append(f'{args.model_dir}:{args.cont_dir}')
	command.append('-e')
	command.append('MODEL_NAME=fashion_mnist')

	if args.tensorboard:
		command.append('-p')
		command.append('8500:8500')
		command.append('-v')
		command.append(f'{args.tb_dir}:{args.cont_tb_dir}')

	if args.session_threads is not None:
		print('Using session parallelism.')
		command.append('-e')
		command.append(f'TENSORFLOW_SESSION_PARALLELISM={args.session_threads}')
	elif args.intra_inter_threads is not None:
		print('Using intra-inter op parallelism.')
		intra, inter = tuple(args.intra_inter_threads)
		command.append('-e')
		command.append(f'TENSORFLOW_INTRA_OP_PARALLELISM={intra}')
		command.append('-e')
		command.append(f'TENSORFLOW_INTER_OP_PARALLELISM={inter}')

	command.append('-e')
	command.append(f'OMP_NUM_THREADS={args.omp_threads}')

	if args.omp_verbose:
		command.append('-e')
		command.append(f'MKLDNN_VERBOSE=1')

	if args.detached:
		command.append('-d')
	
	command.append('-it')
	command.append(f'{args.IMAGE}')

	subprocess.run(args=command)

if __name__ == '__main__':
	main()
