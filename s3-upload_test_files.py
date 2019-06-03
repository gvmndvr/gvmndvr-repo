#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import os

# Create a function to upload files to the S3 bucket
def upload_files(path):
    PROFILE = 'homework'
    BUCKET_NAME = 'ndvr-homework-dataops'

# Create an S3 session.
    session = boto3.session.Session(profile_name=PROFILE)
    s3 = session.resource('s3')

    bucket = s3.Bucket(BUCKET_NAME)
 
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(path)+1:], Body=data)
 
# Invoke the function to upload files to the S3 bucket
# All the files to be uploaded should be in a sub-directory called "files" within the directory where this script resides
if __name__ == "__main__":
#    upload_files('/home/ubuntu/ndvr/files')
    upload_files('./files')
