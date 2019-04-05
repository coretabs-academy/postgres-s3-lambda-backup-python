import datetime, calendar, os
import boto3, botocore

aws_access_key_id = os.environ.get('aws_access_key_id')
aws_secret_access_key = os.environ.get('aws_secret_access_key')

backup_local_path = os.environ.get('backup_local_path')

bucket_name = os.environ.get('bucket_name')
object_name_prefix = os.environ.get('object_name_prefix')

session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3 = session.client('s3')

now = datetime.datetime.now()

object_name = object_name_prefix + '_' + str(now.year) + '_' + calendar.month_name[now.month] + '_' + str(now.day) + '.dump'
s3.delete_object(Bucket=bucket_name, Key=object_name)
try:
    s3.get_object(Bucket=bucket_name, Key=object_name).load()
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == '404':
        print('cleaned s3 previous file')

s3.upload_file(backup_local_path, bucket_name, object_name)

print('done done done')