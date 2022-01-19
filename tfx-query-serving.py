import sys

assert sys.version_info.major == 3

import tensorflow as tf
from   tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np

import os
import random
import json
import csv
import requests
import argparse
import time

print("TensorFlow version: {}".format(tf.__version__))

CLASS_NAMES = [
	'T-shirt/top' ,
	'Trouser'     ,
	'Pullover'    ,
	'Dress'       ,
	'Coat'        ,
	'Sandal'      ,
	'Shirt'       ,
	'Sneaker'     ,
	'Bag'         ,
	'Ankle boot'  ]

REQUEST_URI = 'http://localhost:' \
              '8501/v1/models/fashion_mnist:' \
              'predict'

IMAGES_DIR  = './images'
TIME_DIR    = './time'

BATCH_ITER = 1

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

def get_random_sample(test):
	rando = random.randint(0, len(test['images']) - 1)

	return test['images'][rando], test['labels'][rando]

def random_batch(data, size):
	img_batch = np.ndarray(
		shape = (size, 28, 28, 1)
	)

	label_batch = np.ndarray(shape = (size))

	for id in range(size):
		image, label = get_random_sample(data)

		img_batch[id] = image
		label_batch[id] = label


	return img_batch, label_batch

def query_model(uri, instances):
	headers = {
		'content-type' : 'application/json' }

	query = {
	    'signature_name' : 'serving_default' ,
		'instances'      : instances         }

	data = json.dumps(query)

	start = time.time()
	response = requests.post(
		uri                ,
		headers = headers  ,
		data    = data     )
	end = time.time()

	print('Serving response:', response)
	print(f'Response time: {end - start} seconds')

	return json.loads(response.text)['predictions'], end - start

def save_predicted_images(img_dir, instances, labels, predictions):
	gen_title = "Label: {} --- Prediction: {}"
	for id, (img, label, pred) in enumerate(zip(instances, labels, predictions)):
		title = gen_title.format(
			CLASS_NAMES[np.argmax(pred)],
			CLASS_NAMES[int(label)]
		)

		fig = plt.figure()
		plt.imshow(img.reshape(28, 28))
		plt.axis('off')
		plt.title(f'\n\n{title}', fontdict={'size': 16})

		save_path = os.path.join(img_dir, str(id))
		os.makedirs(os.path.dirname(save_path), exist_ok=True)

		plt.savefig(save_path)
		plt.close(fig)

def save_response_times(time_path, timels):
	os.makedirs(os.path.dirname(time_path), exist_ok=True)

	csvf = open(time_path, 'w+')
	timesum = 0
	for i, time_s in enumerate(timels):
		timesum += time_s
		csvf.write(f'{i + 1},{time_s}\n')

	timesum /= len(timels)
	csvf.write(f'0,{timesum}\n')

	csvf.close()



def get_parser():
	# Parser description and creation.
	desc = "A command interface that sets the parameters to query a TF serving."
	parser = argparse.ArgumentParser(description = desc)

	# Parser argument to select model dir.
	batch_help = "Number of batch instances sent to infer."
	parser.add_argument(
		'-b', '--batch', metavar='batch', help=batch_help,
		nargs='+',
		type=int,
		default=None
	)

	# Parser argument to set number of requests per batch size.
	iter_help = "Number of requests sent per batch size."
	parser.add_argument(
		'-n', '--iter', metavar='iter', help=iter_help,
		type=int,
		default=BATCH_ITER
	)

	# Parser argument to set request URI.
	uri_help = "URI used for REST API HTTP Request."
	parser.add_argument(
		'-u', '--uri', metavar='uri', help=uri_help,
		type=str,
		default=REQUEST_URI
	)

	# Parser argument to set if save predicted images.
	images_help = "Saves predicted images."
	parser.add_argument(
		'-i', '--images', dest='images', help=images_help,
		action='store_true'
	)

	# Parser argument to set directory of predicted images.
	images_dir_help = "Path to host directory where predicted images will be"
	images_dir_help += " saved."
	parser.add_argument(
		'--images-dir', metavar='images_dir', help=images_dir_help,
		type=str,
		default=IMAGES_DIR
	)

	# Parser argument to set if save predicted images.
	time_help = "Saves response times."
	parser.add_argument(
		'-t', '--time', dest='time', help=time_help,
		action='store_true'
	)

	# Parser argument to set directory for response time data.
	time_dir_help = "Path to host directory where response time data will be"
	time_dir_help += " saved"
	parser.add_argument(
		'--time-dir', metavar='time_dir', help=time_dir_help,
		type=str,
		default=TIME_DIR
	)

	return parser

def main():
	parser = get_parser()
	args = parser.parse_args()

	(_, test) = import_mnist_dataset()

	for size in args.batch:
		print(f'Batch Size: {size}')
		timels = []
		for i in range(args.iter):
			instances, labels = random_batch(test, size)
			predictions, time_s = query_model(args.uri, instances.tolist())
			
			timels.append(time_s)

			if args.images:
				img_dir = args.images_dir + f'/batch_{size}/{i + 1}'
				save_predicted_images(img_dir, instances, labels, predictions)

		if args.time:
			time_path = args.time_dir + f'/batch_{size}.csv'
			save_response_times(time_path, timels)


if __name__ == '__main__':
	main()