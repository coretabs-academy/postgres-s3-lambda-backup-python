import os
import paramiko

ssh_key = os.environ.get('ssh_key')
hostname = os.environ.get('hostname')
username = os.environ.get('username')

backup_command = os.environ.get('backup_command')

if False:
    try:
        from dev_secrets import *
    except ModuleNotFoundError:
        pass

printer = lambda msg : print('=' * 10, msg)

def connect_ssh():
    ssh_key_file_path = '/tmp/mykey.ssh'
    if os.path.exists(ssh_key_file_path):
        os.remove(ssh_key_file_path)
    with open(ssh_key_file_path, 'w') as f:
        f.write(ssh_key)
    if not os.path.exists(ssh_key_file_path):
        printer('could NOT write SSH key')
        return {'statusCode': 500, 'body': 'failed, could NOT write SSH key'}

    ssh = paramiko.SSHClient()
    cert = paramiko.RSAKey.from_private_key_file(ssh_key_file_path)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, pkey=cert)

    return ssh


def create_backup_on_server_and_copy_it(ssh):
    printer('running: ' + backup_command)

    stdin, stdout, errors = ssh.exec_command(backup_command)

    printer('outputs')
    stdout.channel.recv_exit_status()
    for line in stdout.readlines():
        print(line)

    printer('errors')
    errors.channel.recv_exit_status()
    lines = errors.readlines()
    for line in lines:
        print(line)


def main(event, context):
    printer('connecting ssh...')
    ssh = connect_ssh()
    
    printer('creating backup...')
    create_backup_on_server_and_copy_it(ssh)

    printer('closing ssh...')
    ssh.close()

    response = {
        'statusCode': 200,
        'body': 'Successfully uploaded backup'
    }

    return response

