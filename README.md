## Postgres to S3 AWS Lambda Backup Function in Python

This function creates backup of your postgres database (running in a server) into s3 bucket by:

1. Going into the server via SSH.
2. Creating a backup with pg_dump and grabing the created dump file.
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

## Samples

### Backup Script

You backup script might differ from our backup script, so we decided to store it in an env_var.

This script will be executed in your VPS via SSH.

Sample script:

```bash
sudo rm -f "/var/academy-db/my_new_academy.dump"

sudo rm -f "/home/ec2-user/academy_backup.dump"

sudo docker exec $(sudo docker ps -a | grep db- | awk '{print $1}') sh -c "pg_dump -U db_user -Fc db_table > /var/lib/postgresql/data/my_new_academy.dump"


sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump"
```

Once you make sure that your script is working properly in the VPS, convert it into a one-liner to run store it as an env_var (**don't forget to escape `$`**):

```bash
sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm -f "/home/ec2-user/academy_backup.dump" && sudo docker exec $(sudo docker ps -a | grep db- | awk '{print \$1}') sh -c "db_user -U db_table -Fc academy_db > /var/lib/postgresql/data/my_new_academy.dump" && sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump"
```

### Sample `.env` file

This file will help you **pass env vars** while you develop locally

```bash
ssh_key = "-----BEGIN RSA PRIVATE KEY-----\n YOUR KEY GOES HERE, should be one liner seperated by \n     \n-----END RSA PRIVATE KEY-----"

hostname = '1.1.1.1'
username = 'ec2-user'
backup_command = 'sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm -f "/home/ec2-user/academy_backup.dump" && sudo docker exec $(sudo docker ps -a | grep db- | awk '{print \$1}') sh -c "pg_dump -U db_user -Fc db_table > /var/lib/postgresql/data/my_new_academy.dump" && sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump"'

backup_local_path = '/tmp/academy_backup.dump'
backup_remote_path = '/home/ec2-user/academy_backup.dump'

aws_access_key_id = 'YOUR AWS ACCESS KEY ID'
aws_secret_access_key = 'YOUR AWS SECRET ACCESS KEY'

bucket_name = 'your-s3-bucket-name'
object_name = 'your-s3-object-name'
```

### Sample `dev_secrets.py` file

This is a handy file to **ensure secrets won't be pushed** into the remote repo.

```python
ssh_key = "-----BEGIN RSA PRIVATE KEY-----\n YOUR KEY GOES HERE, should be one liner seperated by \n     \n-----END RSA PRIVATE KEY-----"

hostname = '1.1.1.1'
username = 'ec2-user'
backup_command = 'sudo rm -f "/var/academy-db/my_new_academy.dump" && sudo rm -f "/home/ec2-user/academy_backup.dump" && sudo docker exec $(sudo docker ps -a | grep db- | awk \'{print $1}\') sh -c "pg_dump -U db_user -Fc db_table > /var/lib/postgresql/data/my_new_academy.dump" && sudo cp "/var/academy-db/my_new_academy.dump" "/home/ec2-user/academy_backup.dump"'

backup_local_path = '/tmp/academy_backup.dump'
backup_remote_path = '/home/ec2-user/academy_backup.dump'

aws_access_key_id = 'YOUR AWS ACCESS KEY ID'
aws_secret_access_key = 'YOUR AWS SECRET ACCESS KEY'

bucket_name = 'your-s3-bucket-name'
object_name = 'your-s3-object-name'
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