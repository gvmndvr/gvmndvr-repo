#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError

PROFILE = 'homework'
BUCKET_NAME = 'ndvr-homework-dataops'
KEY = 'test'

# Create an S3 session.
session = boto3.session.Session(profile_name=PROFILE)
s3 = session.resource('s3')

# Try to download the test object from our bucket. Print an error if it does
# not exist, raise an exception if something else went wrong.
try:
	s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
except ClientError as e:
	if e.response['Error']['Code'] == '404':
		print('The object does not exist.')
	else:
		raise

# Print the contents of the test file.
with open(KEY, 'r') as f:
	print(f.read())
