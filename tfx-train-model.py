import sys

assert sys.version_info.major == 3

import tensorflow as tf
from   tensorflow import keras
from   tensorflow.python.tools import saved_model_cli as sv_cli

import os
import subprocess
import argparse

print("TensorFlow version: {}".format(tf.__version__))

MODEL_DIR = '/tmp/models/fashion_mnist'
MODEL_VERSION = 1
MODEL_EPOCHS = 5

def import_mnist_dataset():
	fashion_mnist = keras.datasets.fashion_mnist
	(train_images , train_labels), \
	(test_images  , test_labels ) = fashion_mnist.load_data()

	# Scale values to 0.0 - 1.0
	train_images = train_images / 255.0
	test_images  = test_images  / 255.0

	# Reshape to fit into model
	train_images = train_images.reshape(
		train_images.shape[0],
		28, 28, 1
	)
	test_images = test_images.reshape(
		test_images.shape[0],
		28, 28, 1
	)

	print(
		'\ntrain_images.shape : {}, of {}'.format(
			train_images.shape ,
			train_images.dtype ))
	print(
		'\ntest_images.shape : {}, of {}'.format(
			test_images.shape ,
			test_images.dtype ))

	return (
		{'images': train_images, 'labels': train_labels} ,
		{'images': test_images , 'labels': test_labels } )

def configure_model(verbose=False):
	model = keras.Sequential([
		keras.layers.Conv2D(
			input_shape = (28,28,1) ,
			filters     = 8         ,
			kernel_size = 3         ,
			strides     = 2         ,
			activation  = 'relu'    ,
			name        = 'Conv1'   ) ,
		keras.layers.Flatten()        ,
		keras.layers.Dense(
			10             ,
			name = 'Dense' )          ,
	])

	model.summary()

	model.compile(
		optimizer = 'adam',
		loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
		metrics = [keras.metrics.SparseCategoricalAccuracy()]
	)

	return model

def save_model(model, dir, version):
	export_path = os.path.join(dir, str(version))
	print('export_path = {}\n'.format(export_path))

	tf.keras.models.save_model(
		model       ,
		export_path ,
		overwrite         = True ,
		include_optimizer = True ,
		save_format       = None ,
		signatures        = None ,
		options           = None )

	print('\nSaved model:')
	subprocess.run(['ls', '-l', export_path])

	return export_path


def get_parser():
	# Parser description and creation.
	desc = "A command interface that sets the parameters for a model to be"
	desc += " trained with 'Fashion MNIST' dataset."
	parser = argparse.ArgumentParser(description = desc)

	# Parser argument to select model dir.
	dir_help = "Path to directory where the trained model version will be"
	dir_help += " saved."
	parser.add_argument(
		'-d', '--dir', metavar='dir', help=dir_help,
		type=str,
		default=MODEL_DIR
	)

	# Parser argument to set model version.
	version_help = "Version number for the trained model."
	parser.add_argument(
		'--version', metavar='version', help=version_help,
		type=int,
		default=MODEL_VERSION
	)

	# Parser argument to set the number of epochs for the training.
	epochs_help = "Number of epochs used in the model training."
	parser.add_argument(
		'-n', '--epochs', metavar='epochs', help=epochs_help,
		type=int,
		default=MODEL_EPOCHS
	)

	return parser

def main():
	parser = get_parser()
	args = parser.parse_args()
	
	(train, test) = import_mnist_dataset()
	model = configure_model()
	
	model.fit(
		train['images']      ,
		train['labels']      ,
		epochs = args.epochs )

	test['loss'], test['acc'] = model.evaluate(test['images'], test['labels'])
	print('\nTest accuracy: {}'.format(test['acc']))

	save_model(
		model   = model        ,
		dir     = args.dir     ,
		version = args.version )

if __name__ == '__main__':
	main()