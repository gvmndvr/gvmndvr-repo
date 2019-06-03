###########
# Background
###########

Most of the technologies for this project were relatively new for me.
Python
MySQL
AWS (EC2, S3, CLI) - Had started an AWS Certification training course  ("AWS Certified Solutions Architect – Associate") on Udemy
Git - Got some exposure in the current project

This situation presented an extremely great opportunity to learn very quickly and I thoroughly enjoyed the effort.


##################
# Environments used
##################

WINS - Windows Personal Laptop
SRCE - Source AWS EC2 Linux (ubuntu) instance with all the tools listed below
TRGT - Target NDVR AWS environment 


############
# Objective
############

## Create a script to enforce the following retention policy: 
OFFICIAL jobs should be kept forever, TRIAL can be purged after 3 months
sourceData files can be purged if no job is referring to them anymore

## Additional Input
A database table with the following fields:
* jobId – a 64 char UUID identifying a job, is unique
* completedAt – timestamp, can be null
* type – string, either ‘OFFICIAL’ or ‘TRIAL’
* sourceData – a 64 char UUID identifying a source data set, not unique

An S3 bucket that contains files, the filename corresponds to the `sourceData` field

### TRGT S3 information
PROFILE = 'homework'
BUCKET_NAME = 'ndvr-homework-dataops'

### TRGT MySQL Connectivity information
PROFILE = 'homework'
REGION = 'us-east-1'
HOST = 'dataops.cnh8zrq6tuc4.us-east-1.rds.amazonaws.com'
PORT = 3306
USER = 'dataops'
DATABASE = 'homework'
CA_BUNDLE = 'rds-combined-ca-bundle.pem'

### TRGT RDS information
RDSHOST='dataops.cnh8zrq6tuc4.us-east-1.rds.amazonaws.com'
USERNAME='dataops'
DATABASE='homework'

TOKEN="$(aws --profile homework \
             rds generate-db-auth-token \
             --hostname ${RDSHOST} \
             --port 3306 \
             --region us-east-1 \
             --username ${USERNAME})"


###########
# Pseudocode
###########

Create connections to S3, RDS MySQL
Generate a list of aws S3 bucket files older than 90 days
Loop through the list and delete the files from the aws S3 bucket
Generate a list of file names in the aws S3 bucket that are not referred by any job
Loop through the list and delete the files from the aws S3 bucket
Close memory structures, Close connection to RDS MySQL


#####################
# Pre-requisite Steps & Test Bed Preparation
#####################
Installed/Configured the following in SRCE
Python 3.7
pip
Pipenv
awscli
boto3
pymysql
mysql-client
mysql-server
winscp (to transfer files between WINS and SRCE)


## Sample Directory Structure and files
### Please substitute the directory names based on your specific environment.
### /home/ubuntu/ndvr  (created on SRCE server)

ndvr $ pwd
/home/ubuntu/ndvr
ndvr $ ls -ltr
total 72
-rwxr--r-- 1 ubuntu ubuntu   657 May 23 12:19 s3.py
-rwxr--r-- 1 ubuntu ubuntu  1186 May 23 12:19 rds.py
-rw-r--r-- 1 ubuntu ubuntu 26016 May 23 12:19 rds-combined-ca-bundle.pem
-rwxr--r-- 1 ubuntu ubuntu   730 May 23 12:19 mysql-connect.sh
-rw-r--r-- 1 ubuntu ubuntu  2129 May 30 23:06 ndvr_jobs.csv
-rw-r--r-- 1 ubuntu ubuntu  3979 May 31 00:13 ndvr_jobs_with_uuid_string.csv
drwxrwxr-x 2 ubuntu ubuntu  4096 Jun  3 03:30 files
-rwxr--r-- 1 ubuntu ubuntu   915 Jun  3 03:44 s3-upload_test_files.py
-rwxr--r-- 1 ubuntu ubuntu  4553 Jun  3 04:59 aws-s3-bucket-retention-policy.py
-rwxr--r-- 1 ubuntu ubuntu  2011 Jun  3 05:00 files_not_referred_by_any_job.sh
-rw-rw-r-- 1 ubuntu ubuntu   475 Jun  3 05:27 current_s3_file_list.txt

#### Note: 
rds-combined-ca-bundle.pem is shown in the listing above, but is not added to github repository
current_s3_file_list.txt is dynamically created during the execution of aws-s3-bucket-retention-policy.py
ndvr_jobs_with_uuid_string.csv file was created manually after populating the data in a local MySQL table
Additionally AWS Keys are required to connect to AWS

### /home/ubuntu/ndvr/files (created on SRCE server)
All the test files that get uploaded to the aws S3 bucket as part of testing should be in the "files" sub-directory under the directory where the scripts are located.

#### Note:
These files were uploaded to the aws S3 bucket using s3-upload_test_files.py

files $ pwd
/home/ubuntu/ndvr/files
files $ ls -ltr
total 192
-rw-rw-r-- 1 ubuntu ubuntu 60 May 29 02:47 test_1.txt
-rw-rw-r-- 1 ubuntu ubuntu 60 May 29 02:48 test_2.txt
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000002
-rw-r--r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000001
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000005
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000004
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000003
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000008
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000007
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000006
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000011
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000010
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000009
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000014
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000013
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000012
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000017
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000016
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000015
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000019
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000018
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000022
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000021
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000020
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000025
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000024
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000023
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000027
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000026
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000030
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000029
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000028
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000033
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000032
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000031
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000035
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000034
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000038
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000037
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000036
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000041
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000040
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000039
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000043
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000042
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000045
-rw-rw-r-- 1 ubuntu ubuntu 21 May 31 02:28 incoming_000044
-rw-rw-r-- 1 ubuntu ubuntu 46 Jun  2 02:42 test
files $



## Tables
### TRGT MySQL 
#### Table Name : ndvr_job_status
CREATE TABLE ndvr_job_status
(
    jobId                varchar(64) NOT NULL ,
    completedAt          timestamp   NULL,
    type                 varchar(12),
    sourceData           varchar(64) NOT NULL,
    PRIMARY KEY (jobId)
);

    Got an error when I tried to create it in TRGT MySQL. 

mysql> CREATE TRIGGER before_insert_job_status
    ->   BEFORE INSERT ON job_status
    ->   FOR EACH ROW
    ->   SET new.jobId = uuid();
ERROR 1419 (HY000): You do not have the SUPER privilege and binary logging is enabled (you *might* want to use the less safe log_bin_trust_function_creators variable)

Had to follow the method listed below to load test data into TRGT MySQL


##### Method used to populate test data into ndvr_job_status table in TRGT MySQL : 
    Created a csv file (ndvr_jobs_with_uuid_string.csv) using data from ndvr_jobs table SRCE MySQL. 
    Used MySQL LOAD utility to load the csv file into ndvr_job_status table in TRGT MySQL.

LOAD DATA LOCAL INFILE '/home/ubuntu/ndvr/ndvr_jobs_with_uuid_string.csv' 
INTO TABLE ndvr_job_status FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'
 (jobId,completedAt, type,sourceData);

commit;



mysql> describe ndvr_job_status
    -> ;
+-------------+-------------+------+-----+---------+-------+
| Field       | Type        | Null | Key | Default | Extra |
+-------------+-------------+------+-----+---------+-------+
| jobId       | varchar(64) | NO   | PRI | NULL    |       |
| completedAt | timestamp   | YES  |     | NULL    |       |
| type        | varchar(12) | YES  |     | NULL    |       |
| sourceData  | varchar(64) | NO   |     | NULL    |       |
+-------------+-------------+------+-----+---------+-------+
4 rows in set (0.01 sec)



## Load ndvr_job_status table in TRGT
ndvr $ pwd
/home/ubuntu/ndvr
ndvr $ ./mysql-connect.sh

mysql> LOAD DATA LOCAL INFILE '/home/ubuntu/ndvr/ndvr_jobs_with_uuid_string.csv' 
INTO TABLE ndvr_job_status FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'
 (jobId,completedAt, type,sourceData);


mysql> select * from ndvr_job_status;
+--------------------------------------+---------------------+----------+-----------------+
| jobId                                | completedAt         | type     | sourceData      |
+--------------------------------------+---------------------+----------+-----------------+
| f6deca8c-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:00 | OFFICIAL | incoming_000001 |
| f6decc8a-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:01 | OFFICIAL | incoming_000002 |
| f6ded3dd-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:02 | OFFICIAL | incoming_000003 |
| f6ded4b6-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:03 | OFFICIAL | incoming_000004 |
| f6ded538-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:04 | OFFICIAL | incoming_000005 |
| f6ded5b4-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:05 | OFFICIAL | incoming_000006 |
| f6ded629-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:06 | OFFICIAL | incoming_000007 |
| f6ded69b-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:07 | OFFICIAL | incoming_000008 |
| f6ded74b-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:08 | OFFICIAL | incoming_000009 |
| f6ded7be-832f-11e9-a797-0ae8fa97339a | NULL                | TRIAL    | incoming_000010 |
| f6ded832-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:10 | TRIAL    | incoming_000011 |
| f6ded8a2-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:11 | TRIAL    | incoming_000012 |
| f6ded913-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:12 | TRIAL    | incoming_000013 |
| f6ded982-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:13 | TRIAL    | incoming_000014 |
| f6ded9f2-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:14 | TRIAL    | incoming_000015 |
| f6deda53-832f-11e9-a797-0ae8fa97339a | NULL                | TRIAL    | incoming_000016 |
| f6dedabd-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:16 | TRIAL    | incoming_000017 |
| f6dedb2e-832f-11e9-a797-0ae8fa97339a | 2019-01-01 12:30:17 | TRIAL    | incoming_000018 |
| f6dedb9e-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:00 | OFFICIAL | incoming_000019 |
| f6dedc0c-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:01 | OFFICIAL | incoming_000020 |
| f6dedc7a-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:02 | OFFICIAL | incoming_000021 |
| f6dedce8-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:03 | OFFICIAL | incoming_000022 |
| f6dedd56-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:04 | OFFICIAL | incoming_000023 |
| f6deddc3-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:05 | OFFICIAL | incoming_000024 |
| f6dede2f-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:06 | OFFICIAL | incoming_000025 |
| f6dede9c-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:07 | OFFICIAL | incoming_000026 |
| f6dedf0a-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:08 | OFFICIAL | incoming_000027 |
| f6dedf76-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:09 | OFFICIAL | incoming_000028 |
| f6dedfe4-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:10 | OFFICIAL | incoming_000029 |
| f6dee054-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:11 | OFFICIAL | incoming_000030 |
| f6dee0c1-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:12 | TRIAL    | incoming_000031 |
| f6dee12e-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:13 | TRIAL    | incoming_000032 |
| f6dee19b-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:14 | TRIAL    | incoming_000033 |
| f6dee20a-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:15 | TRIAL    | incoming_000034 |
| f6dee277-832f-11e9-a797-0ae8fa97339a | 2019-04-01 12:30:16 | TRIAL    | incoming_000035 |
| f6dee2e2-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:17 | TRIAL    | incoming_000036 |
| f6dee34f-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:18 | TRIAL    | incoming_000037 |
| f6dee3be-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:19 | TRIAL    | incoming_000038 |
| f6dee42a-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:20 | TRIAL    | incoming_000039 |
| f6dee497-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:21 | TRIAL    | incoming_000040 |
| f6dee508-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:22 | TRIAL    | incoming_000041 |
| f6dee575-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:23 | TRIAL    | incoming_000042 |
| f6deea1f-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:24 | TRIAL    | incoming_000043 |
| f6deeaf3-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:25 | TRIAL    | incoming_000044 |
| f6deeb6d-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:26 | TRIAL    | incoming_000045 |
| f6deebdc-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:27 | TRIAL    | incoming_000045 |
| f6deec4a-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:28 | TRIAL    | incoming_000045 |
| f6deecb7-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:29 | TRIAL    | incoming_000045 |
| f6deed22-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:30 | TRIAL    | incoming_000045 |
| f6deed8d-832f-11e9-a797-0ae8fa97339a | 2019-01-05 12:30:31 | TRIAL    | incoming_000045 |
+--------------------------------------+---------------------+----------+-----------------+
50 rows in set (0.01 sec)

mysql> commit;


####  Table Name : current_s3_file_list
CREATE  TABLE current_s3_file_list
(
    sourceData            varchar(64) NOT NULL
);

##### Note: The load will have unexpected results if you open the csv file using Excel, after saving. Excel converts the text data to a date format altering the data.  Before opening the csv file, check the link below for instructions on how to open it without altering the data.
https://answers.microsoft.com/en-us/msoffice/forum/all/excel-2010-always-changing-to-date-format-after/8ca5cad8-3aae-4288-a288-d7324a55fedf


## Execution of aws S3 bucket file retention policy script

1. Upload test files to aws S3 bucket
ndvr $ pwd
/home/ubuntu/ndvr
ndvr $ pipenv run ./s3-upload_test_files.py

2. List the files in the aws s3 bucket
ndvr $ pwd
/home/ubuntu/ndvr
ndvr $ aws --profile homework s3 ls ndvr-homework-dataops

3. Execute the aws S3 bucket file retention policy script
ndvr $ pwd
/home/ubuntu/ndvr
ndvr $ ./aws-s3-bucket-retention-policy.py
*******************************************
Deleting the following files from S3 bucket ndvr-homework-dataops with ndvr_job_status.completedAt date 90 days prior to today's date
*******************************************
incoming_000011
incoming_000012
incoming_000013
incoming_000014
incoming_000015
incoming_000017
incoming_000018
incoming_000036
incoming_000037
incoming_000038
incoming_000039
incoming_000040
incoming_000041
incoming_000042
incoming_000043
incoming_000044
incoming_000045
mysql: [Warning] Using a password on the command line interface can be insecure.
*******************************************
Deleting the following files from S3 bucket ndvr-homework-dataops that is not referred by any job
*******************************************
test
test_1.txt
test_2.txt
*******************************************
Finally - Close Cursor, Closed  Connection
*******************************************
ndvr $


## Assumptions, Limitations and opportunity for potential improvements
In the interest of time, some short cuts were taken. There is definitely more opportunity to make the design and the scripts more robust.

### The age of the files to be purged is not determined using the date/time stamp of the file at the bucket level, it's determined by the "completedAt" value for each file in ndvr_job_status table.

### UUID 
Though the jobId column in 64 characters long, I decided to go with the UUID() that generates 32 character strings with 4 dashes/hyphens in between.

### Error Handling
This version has limited error handling.

### ndvr_job_status table
Unless the file names are going to remain the same, or there are other requirements that warrants keeping all the rows in ndvr_job_status table, we may have to implement logic to purge rows where the column values for sourceData  matches the file names of the files that were deleted from the aws s3 bucket.

### Automation has not addressed
