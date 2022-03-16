import subprocess

def generate_prom_yaml(config_dir, config_scrape, config_yaml='prometheus.yml'):
	import os
	import yaml
	config_dict = {}
	if config_scrape:
		config_dict['scrape_configs'] = config_scrape

	config_path = os.path.join(config_dir, config_yaml)
	os.makedirs(os.path.dirname(config_path), exist_ok=True)
	with open(config_path, 'w') as config_file:
		yaml.dump(config_dict, config_file)

	return config_path

def deploy_prometheus(
		prom_config ,

		config_path          = '/tmp/prometheus.yml' ,
		config_job_name      = None                  ,
		config_target        = None                  ,
		config_metrics_path  = None                  ,

		host_prom_path = None ,
		cont_prom_path = '/etc/prometheus/prometheus.yml' ,
		prom_image     = 'prom/prometheus'                ,
		prom_port      = 9090                             ,
		prom_cpus      = None                             ,
		
		cont_detached = True ,
		cont_name     = None ):
	PROMETHEUS_PORT = 9090

	if prom_config == 'generate':
		scrape_dict = {}
		if config_job_name is not None:
			scrape_dict['job_name'] = config_job_name
		if config_target is not None:
			scrape_dict['static_configs'] = [{'targets' : [config_target]}]
		if config_metrics_path is not None:
			scrape_dict['metrics_path'] = config_metrics_path
		
		host_prom_path = generate_prom_yaml(config_path, scrape_dict)
	
	if prom_config == 'load':
		pass

	if host_prom_path is not None:
		prom_cmd = []
		prom_cmd.append('docker')
		prom_cmd.append('run')
		prom_cmd.append('-p')
		prom_cmd.append(f'{prom_port}:{PROMETHEUS_PORT}')
		prom_cmd.append('-v')
		prom_cmd.append(f'{host_prom_path}:{cont_prom_path}')
		
		if prom_cpus is not None:
			prom_cmd.append('--cpuset-cpus')
			prom_cmd.append(prom_cpus)

		if cont_name is not None:
			prom_cmd.append('--name')
			prom_cmd.append(cont_name)
		if cont_detached:
			prom_cmd.append('-d')

		prom_cmd.append('-it')
		prom_cmd.append(prom_image)

		subprocess.run(args=prom_cmd)
	
def deploy_serving(
		tfserving_image ,

		model_name         ,
		host_model_dir     ,
		cont_model_dir     ,
		model_port  = 8501 ,

		tensorboard = False              ,
		host_tb_dir = '/tmp/tensorboard' ,
		cont_tb_dir = '/tmp/tensorboard' ,
		tb_port     = 8500               ,

		cont_cpus   = None ,
		
		parallelism     = None  ,
		omp_threads     = None  ,
		omp_verbose     = False ,
		session_threads = None  ,
		intra_threads   = None  ,
		inter_threads   = None  ,
 
		cont_detached = True        ,
		cont_name     = None ):
	TFSERVING_MODEL_PORT = 8501
	TFSERVING_TENSORBOARD_PORT = 8500

	model_cmd = []
	model_cmd.append('docker')
	model_cmd.append('run')
	model_cmd.append('-p')
	model_cmd.append(f'{model_port}:{TFSERVING_MODEL_PORT}')
	model_cmd.append('-v')
	model_cmd.append(f'{host_model_dir}:{cont_model_dir}')
	model_cmd.append('-e')
	model_cmd.append(f'MODEL_NAME={model_name}')

	if tensorboard:
		model_cmd.append('-p')
		model_cmd.append(f'{tb_port}:{TFSERVING_TENSORBOARD_PORT}')
		model_cmd.append('-v')
		model_cmd.append(f'{host_tb_dir}:{cont_tb_dir}')

	if cont_cpus is not None:
		model_cmd.append('--cpuset-cpus')
		model_cmd.append(cont_cpus)

	if parallelism is not None:
		if omp_threads is not None:
			model_cmd.append('-e')
			model_cmd.append(f'OMP_NUM_THREADS={omp_threads}')
		if omp_verbose:
			model_cmd.append('-e')
			model_cmd.append('MKLDNN_VERBOSE=1')

		if parallelism == 'session_threads':
			model_cmd.append('-e')
			model_cmd.append(f'TENSORFLOW_SESSION_PARALELLISM={session_threads}')
		elif parallelism == 'intra_inter_threads':
			model_cmd.append('-e')
			model_cmd.append(f'TENSORFLOW_INTRA_OP_PARALLELISM={intra_threads}')
			model_cmd.append('-e')
			model_cmd.append(f'TENSORFLOW_INTER_OP_PARALLELISM={inter_threads}')

	if cont_name is not None:
		model_cmd.append('--name')
		model_cmd.append(cont_name)
	if cont_detached:
		model_cmd.append('-d')

	model_cmd.append('-it')
	model_cmd.append(tfserving_image)

	subprocess.run(args=model_cmd)
