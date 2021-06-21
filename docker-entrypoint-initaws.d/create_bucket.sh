#!/bin/bash
set -x
awslocal s3 mb s3://mybucket
set +x

# aws configure set aws_access_key_id test
# aws configure set aws_secret_access_key test
# awslocal s3 mb s3://mybucket
