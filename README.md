## Postgres to S3 AWS Lambda Backup Function in Python

This function creates backup of your postgres database (running in a server) into s3 bucket by:

1. Going into the server via SSH.
2. Creating a backup with pg_dump.
3. Uploading the dump file into S3.

## Scheduling

The `serverless.yml` file contains how the lambda function is triggered.

To run the backup function every 10 mins:

```yml
functions:
  main:
    handler: handler.main
    events:
     - schedule: rate(10 minutes)
```

To see more on scheduling lambda functions, [follow this link](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)

## Samples

### Uploader Script

The file `uploader.py` contains the uploading code into S3 from the server that will be connected to using SSH.

You will embed this file code into your backup script using `printf`.

### Backup Script

You backup script might differ from our backup script, so we decided to store it in an env_var.

This script will be executed in your VPS via SSH.

Sample script:

```bash
sudo rm -f "/var/academy-db/my_new_academy.dump"

sudo rm -f "/home/ec2-user/academy_backup.dump"

sudo docker exec $(sudo docker ps -a | grep db- | awk '{print $1}') sh -c "pg_dump -U db_user -Fc db_table > /var/lib/postgresql/data/my_new_academy.dump"


sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump"

export aws_access_key_id="YOUR AWS ACCESS KEY ID"
export aws_secret_access_key="YOUR AWS SECRET ACCESS KEY"
export backup_local_path="/home/ec2-user/academy_backup.dump"
export bucket_name="your-s3-bucket-name"
export object_name_prefix="your-s3-object-name-prefix"

printf "import datetime, calendar, os\nimport os... your uploader script each line seperated with \n" > /home/ec2-user/uploader.py

sudo pip install boto3
python /home/ec2-user/uploader.py

unset aws_access_key_id
unset aws_secret_access_key
unset backup_local_path
unset bucket_name
unset object_name_prefix
```

Once you make sure that your script is working properly in the VPS, convert it into a one-liner to run store it as an env_var (**don't forget to escape `$`**):

```bash
sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm -f "/home/ec2-user/academy_backup.dump" && sudo docker exec $(sudo docker ps -a | grep db- | awk '{print \$1}') sh -c "pg_dump -U academy_user -Fc academy_db > /var/lib/postgresql/data/my_new_academy.dump" && sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump" && export aws_access_key_id="YOUR AWS ACCESS KEY ID" && export aws_secret_access_key="YOUR AWS SECRET ACCESS KEY" && export backup_local_path="/home/ec2-user/academy_backup.dump" && export bucket_name="your-s3-bucket-name" && export object_name_prefix="your-s3-object-name-prefix" && printf "import datetime, calendar, os\nimport boto3, botocore\naws_access_key_id = os.environ.get('aws_access_key_id')\naws_secret_access_key = os.environ.get('aws_secret_access_key')\nbackup_local_path = os.environ.get('backup_local_path')\nbucket_name = os.environ.get('bucket_name')\nobject_name_prefix = os.environ.get('object_name_prefix')\nsession = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)\ns3 = session.client('s3')\nnow = datetime.datetime.now()\nobject_name = object_name_prefix + '_' + str(now.year) + '_' + calendar.month_name[now.month] + '_' + str(now.day) + '.dump'\ns3.delete_object(Bucket=bucket_name, Key=object_name)\ntry:\n    s3.get_object(Bucket=bucket_name, Key=object_name).load()\nexcept botocore.exceptions.ClientError as e:\n    if e.response['Error']['Code'] == '404':\n        print('cleaned s3 previous file')\ns3.upload_file(backup_local_path, bucket_name, object_name)\nprint('uploaded successfully to S3, tadaaaa!')" > /home/ec2-user/uploader.py && sudo pip install boto3 && python /home/ec2-user/uploader.py && unset aws_access_key_id && unset aws_secret_access_key && unset backup_local_path && unset bucket_name && unset object_name_prefix
```

### Sample `.env` file

This file will help you **pass env vars** while you develop locally

```bash
ssh_key = "-----BEGIN RSA PRIVATE KEY-----\n YOUR KEY GOES HERE, should be one liner seperated by \n     \n-----END RSA PRIVATE KEY-----"

hostname = '1.1.1.1'
username = 'ec2-user'
backup_command = 'sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm... your one-liner script'
```

### Sample `dev_secrets.py` file

This is a handy file to **ensure secrets will NOT be pushed** into the remote repo.

```python
ssh_key = "-----BEGIN RSA PRIVATE KEY-----\n YOUR KEY GOES HERE, should be one liner seperated by \n     \n-----END RSA PRIVATE KEY-----"

hostname = '1.1.1.1'
username = 'ec2-user'
backup_command = 'sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm ... your one-liner script'
```

## Local Development



### Installing dependencies

You need to install the dependencies simply by to be able to do `sls deploy` or `sls offline`:

```bash
npm install
```

### Running with SLS Offline

To try the function locally, you will need to change the trigger in the `serverless.yml` file into:

```yml
functions:
  main:
    handler: handler.main
    events:
      - http:
          path: /
          method: get
```

After you run `sls offline` in the terminal, you can simply run the function from the browser in the url: [http://localhost:3000](http://localhost:3000)

## Deployment

First, **make sure you filled the file `.env`** with the correct environment variables.

Then, simply run this command:

```bash
sls deploy --stage production
```

It will deploy the function on us-east-2 region (as specified in the `serverless.yml`), to run the function:

```bash
sls invoke -f main --stage production
```