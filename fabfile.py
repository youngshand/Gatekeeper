from fabric.api import env, hosts, run, local, task, sudo
from fabric.utils import abort
from fabric.context_managers import cd, settings

account_name = 'gatekeeper'
repo_url = '<url for the repo e.g. git@github.com:example_user/example_repo>'
number_of_processes = '1'

env.user = account_name
env.sudo_user = account_name
env.hosts = ['<hostname for the server>']

@task
def deploy():

	with cd('/home/%s' % account_name):
		run('git pull origin master')
		run('source env/bin/activate')
		run('env/bin/pip install -r requirements.txt')

	with settings(user = 'root'):
		run('supervisorctl stop %s' % account_name)
		run('supervisorctl start %s' % account_name)

@task
def create():

	env.user = 'root'

	run("adduser %s --disabled-password --no-create-home --gecos ''" % account_name)
	run('git clone %s /home/%s' % (repo_url, account_name))

	run('mkdir /home/%s/.ssh' % account_name)

	with cd("/home/%s/.ssh/" % account_name):
		run("cp /root/.ssh/id_rsa* .")
		run("curl http://keys.beingbui.lt/base >> authorized_keys")
		run("chown -R %s:%s /home/%s/.ssh/" % (account_name, account_name, account_name))

	run("echo '%s' > /etc/supervisor/conf.d/%s.conf" % (create_supervisor_config(), account_name))

	with cd('/home/%s' % account_name):
		run('virtualenv env --no-site-packages')
		run('chown -R %s:%s /home/%s' % (account_name, account_name, account_name))
		with settings(user = account_name):
			run('source env/bin/activate')
			run('env/bin/pip install -r requirements.txt')
			run('mkdir logs')
			run('touch logs/stderr.log logs/stdout.log')

	run('supervisorctl reread')
	run('supervisorctl add %s' % account_name)

def create_supervisor_config():
	return SUPERVISOR_CONFIG.format(account_name = account_name, number_of_processes = number_of_processes)


SUPERVISOR_CONFIG = """\
[program:{account_name}]
command=bash {account_name}.bash
process_name={account_name}
numprocs={number_of_processes}
directory=/home/{account_name}/
autostart=true
autorestart=true
user=gatekeeper
stdout_logfile=/home/{account_name}/logs/stdout.log
stdout_logfile_maxbytes=10MB
stderr_logfile=/home/{account_name}/logs/stderr.log
stderr_logfile_maxbytes=10MB\
"""