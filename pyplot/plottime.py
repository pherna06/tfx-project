import numpy as np
import matplotlib.pyplot as plt

import argparse
import json
import os

"""
Posiciones:
0 -> Step
1 -> state
2 (3) -> interval [no usar]
4 -> reward
5 -> acc_reward
6 -> freqpos
7 -> frequency
8 -> power
"""

def get_json_config(json_path):
	with open(json_path, 'r') as jsonf:
		return json.load(jsonf)


def get_file_data(csv_path):
	with open(csv_path, 'r') as csvf:
		csvflines = csvf.readlines()
	
	data = {}
	for line in csvflines:
		id, value =  line.strip('\n[]').split(',')

		data[id] = float(value)
		
	return data, len(csvflines)


def get_parser():
	# Parser description and creation.
	desc = "A command interface that sets the parameters to query a TF serving."
	parser = argparse.ArgumentParser(description = desc)

	# Parser argument to select model dir.
	config_help = "Plot config JSON file."
	parser.add_argument(
		'config_json', help=config_help,
		type=str
	)

	return parser

def main():
	parser = get_parser()
	args = parser.parse_args()

	if args.config_json == None:
		print("No config file!")
		return

	config = get_json_config(args.config_json)

	fig = plt.figure(figsize=(8,6), dpi=150)
	ax = fig.add_subplot(111)

	X = config['in']['xticks']
	Y = config['in']['yticks']
	means = []
	for csv_name, size in zip(config['in']['files'], X):
		csv_path = os.path.join(config['in']['dir'], csv_name)
		csv_data, count = get_file_data(csv_path)

		for i in range(1, count):
			y = csv_data[str(i)] * 1000
			if (y <= Y[-1]):
				plt.scatter(
					[size], [y],
					s=4,
					color='cyan',
				)

		means.append(csv_data['0'] * 1000)

	plt.plot(
		X, means,
		linestyle = '-',
		linewidth = 1,
		marker = 'o',
		alpha = 1.0,
		color='blue'
	)

	# Eje X
	ax.set_xlabel('Batch size')
	ax.set_xticks(X)
	ax.set_xticklabels(X, rotation = 45)

	# Eje Y
	ax.set_ylabel('Response Time (ms)')
	ax.set_yticks(Y)

	# Grid de la gráfica
	ax.grid(
		alpha = 0.25,
		linestyle = ':'
	)

	save_path = os.path.join(config['out']['dir'], config['out']['name'])
	os.makedirs(os.path.dirname(save_path), exist_ok=True)
	plt.savefig(save_path, bbox_inches='tight')


if __name__ == '__main__':
	main()