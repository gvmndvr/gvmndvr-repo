#!/usr/bin/env python3
#*********************************************************************************
# Author    : Gheevarghese (George) Muthalaly
# Created   : June 02, 2019
# Purpose   : Implement an aws S3 bucket file retention policy utilizing metadata
#           : stored in a MySQL table
#
# Modification History
# Date                 Name                      Description
#
#*********************************************************************************
import boto3
from botocore.exceptions import ClientError
#from boto.s3.key import Key

import os
import pymysql
import csv

#import warnings

PROFILE = 'homework'
BUCKET_NAME = 'ndvr-homework-dataops'

REGION = 'us-east-1'
HOST = 'dataops.cnh8zrq6tuc4.us-east-1.rds.amazonaws.com'
PORT = 3306
USER = 'dataops'
DATABASE = 'homework'
CA_BUNDLE = 'rds-combined-ca-bundle.pem'

###################################
# Create an S3 session
###################################
session = boto3.session.Session(profile_name=PROFILE)
s3 = session.resource('s3')
s3client = boto3.client('s3')

###################################
# Create a new RDS client in the specified region.
###################################
session = boto3.session.Session(profile_name=PROFILE)
client = session.client('rds', region_name=REGION)

###################################
# Get an auth token from IAM. By default it has 15 min TTL
###################################

token = client.generate_db_auth_token(HOST, PORT, USER)

# SSL options specify the filename of the bundle of AWS public keys. The file
# should be in the same directory as this script.
ssl = {'ca': CA_BUNDLE}

###################################
# Create the MySQL connection
###################################
conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=token, db=DATABASE, ssl=ssl)

###################################
# Generate the list of aws S3 bucket files with ndvr_job_status.completedAt date 90 days prior to today's date 
# Loop through the list of files, print their names to stdout and delete them from the aws S3 bucket
###################################
try:
    with conn.cursor() as cursor:
        # Query SSL settings.
        sql1 = "select distinct TRIM(both '()' from sourceData) from ndvr_job_status where type like 'TRIAL' AND timestampdiff(DAY,completedAt,CURRENT_TIMESTAMP) > 90 ;"
        cursor.execute(sql1)
        print("*******************************************")
        print("Deleting the following files from S3 bucket " + BUCKET_NAME + " with ndvr_job_status.completedAt date 90 days prior to today's date")
        print("*******************************************")

        for fileName in cursor.fetchall():
            print(fileName[0])
#
            s3.Object(BUCKET_NAME, fileName[0]).delete()

    current_s3_file_list = 'aws --profile homework s3 ls ndvr-homework-dataops | awk \'{print $4}\' > current_s3_file_list.txt'
    os.system(current_s3_file_list)

###################################
# Call files_not_referred_by_any_job.sh to load data into the table current_s3_file_list from current_s3_file_list.txt
###################################
    os.system("./files_not_referred_by_any_job.sh")
    conn.commit()

###################################
# After deleting the aws S3 bucket files that are more than 90 days old we need to delete the files that are not referred by a job
# File names in current_s3_file_list table minus file names in ndvr_job_status table are the files that are not referred by a job 
# and needs to be deleted
# Loop through the list and delete the aws S3 bucket files
###################################
    with conn.cursor() as cursor:
        sql3 = "select distinct sourceData  from current_s3_file_list LEFT join ndvr_job_status USING(sourceData) WHERE ndvr_job_status.sourceData is null;"
        cursor.execute(sql3)
        print("*******************************************")
        print("Deleting the following files from S3 bucket " + BUCKET_NAME + " that is not referred by any job")
        print("*******************************************")
        for otherFileNames in cursor.fetchall():
            print(otherFileNames[0])
            s3.Object(BUCKET_NAME, otherFileNames[0]).delete()

except Exception as e:
    print("Within Exception - Check Error Message")
    raise

finally:
    conn.commit()
    cursor.close()
    conn.close()
    print("*******************************************")
    print("Finally - Close Cursor, Closed  Connection")
    print("*******************************************")
   