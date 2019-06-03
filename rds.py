#!/usr/bin/env python3

import boto3
import pymysql

PROFILE = 'homework'
REGION = 'us-east-1'
HOST = 'dataops.cnh8zrq6tuc4.us-east-1.rds.amazonaws.com'
PORT = 3306
USER = 'dataops'
DATABASE = 'homework'
CA_BUNDLE = 'rds-combined-ca-bundle.pem'

# Create a new RDS client in the specified region.
session = boto3.session.Session(profile_name=PROFILE)
client = session.client('rds', region_name=REGION)

# Get an auth token from IAM. By default it has 15 min TTL.
token = client.generate_db_auth_token(HOST, PORT, USER)

# SSL options specify the filename of the bundle of AWS public keys. The file
# should be in the same directory as this script.
ssl = {'ca': CA_BUNDLE}

# Create the MySQL connection.
conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=token, db=DATABASE, ssl=ssl)

# Print SSL settings to verify the connection.
# See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.AWSCLI.html
try:
    with conn.cursor() as cursor:
        # Query SSL settings.
        sql = "show status like 'Ssl%';"
        cursor.execute(sql)
        for setting in cursor.fetchall():
            print(setting)
finally:
    conn.close()
