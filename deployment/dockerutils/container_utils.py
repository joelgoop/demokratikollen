from docker import Client

cli = Client(base_url='unix://var/run/docker.sock')

def isContainerPresent(name):
	containers = cli.containers(all=True)

	for container in containers:
		if name in container['Names'][0]:
			return True

	return False

def remove_offline_containers():
	containers = cli.containers(all=True)

	containers_to_remove = []
	for container in containers:
		if container['Status'].startswith("Exited"):
			containers_to_remove.append(container["Id"])

	for container_id in containers_to_remove:
		cli.remove_container(container_id)

	return containers_to_remove

def get_container_volumes(container):
	info = cli.inspect_container(container)

	return info['Volumes']

def run_command_in_container(container, command, log=None):

	for line in cli.execute(container, command,stream=True):
		# look for erros?
		if 'Traceback' in str(bytes) or 'ERROR' in str(bytes):
			raise Exception
			
		if log:
			try:
				log.info(line.decode("UTF-8").strip())
			except Exception:
				pass
		