#!/usr/bin/env bash

# See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.AWSCLI.html
# for more details on connecting to RDS with IAM credentials.

RDSHOST='dataops.cnh8zrq6tuc4.us-east-1.rds.amazonaws.com'
USERNAME='dataops'
DATABASE='homework'

TOKEN="$(aws --profile homework \
			 rds generate-db-auth-token \
			 --hostname ${RDSHOST} \
			 --port 3306 \
			 --region us-east-1 \
			 --username ${USERNAME})"

# The `rds-combined-ca-bundle.pem` file must be in the same folder as this
# script.
mysql --host="${RDSHOST}" \
	  --port=3306 \
	  --ssl-ca=rds-combined-ca-bundle.pem \
	  --enable-cleartext-plugin \
	  --user="${USERNAME}" \
	  --password="${TOKEN}" \
	  "${DATABASE}"
