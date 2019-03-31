import json, os
import paramiko
import boto3, botocore

ssh_key = os.environ.get('ssh_key')
hostname = os.environ.get('hostname')
username = os.environ.get('username')

backup_local_path = os.environ.get('backup_local_path')
backup_remote_path = os.environ.get('backup_remote_path')
backup_command = os.environ.get('backup_command')

aws_access_key_id = os.environ.get('aws_access_key_id')
aws_secret_access_key = os.environ.get('aws_secret_access_key')

bucket_name = os.environ.get('bucket_name')
object_name = os.environ.get('object_name')

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

    ssh = paramiko.SSHClient()
    cert = paramiko.RSAKey.from_private_key_file(ssh_key_file_path)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, pkey=cert)

    return ssh


def create_backup_on_server_and_copy_it(ssh):
    printer('running: ' + backup_command)

    stdin, stdout, errors = ssh.exec_command(backup_command)

    # delete previous local backup, try three times
    three_times_counter = 0
    while os.path.exists(backup_local_path) and three_times_counter < 3:
        os.remove(backup_local_path)
        three_times_counter += 1

    if three_times_counter == 3:
        printer('could NOT delete the previous backup')
        return {'statusCode': 500, 'body': 'failed, previous backup could NOT be deleted locally'}

    sftp = ssh.open_sftp()
    sftp.get(localpath=backup_local_path, remotepath=backup_remote_path)
    sftp.close()

    printer('outputs')
    stdout.channel.recv_exit_status()
    for line in stdout.readlines():
        print(line)

    printer('errors')
    errors.channel.recv_exit_status()
    lines = errors.readlines()
    for line in lines:
        print(line)


def upload_backup_to_s3():
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key
                           )
    s3 = session.client('s3')

    # delete previous backup
    s3.delete_object(Bucket=bucket_name, Key=object_name)
    try:
        s3.get_object(Bucket=bucket_name, Key=object_name).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            printer('cleaned s3 previous file')
    
    s3.upload_file(backup_local_path, bucket_name, object_name)
    printer('uploaded successfully to S3, tadaaaa!')


def main(event, context):
    printer('connecting ssh...')
    ssh = connect_ssh()
    
    printer('creating backup...')
    create_backup_on_server_and_copy_it(ssh)

    printer('closing ssh...')
    ssh.close()
    
    if os.path.exists(backup_local_path):
        printer('we got the backup, uploading...')
    upload_backup_to_s3()

    response = {
        "statusCode": 200,
        "body": 'Successfully uploaded backup'
    }

    return response

