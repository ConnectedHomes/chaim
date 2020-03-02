#!/bin/bash
#
if [ $# -ne 2 ]
then
  echo "Need an AWS account name and bucket name to build chaim in"
  exit 0
fi
#
AccountName=$1
BucketName=$2
StackName='ian-test-chaim'
MyDir=${0%/*}
if [ ! -e ${MyDir}/chaim_install_master.yaml ]
then
  echo "chaim_install_master.yaml is missing from this directory"
  exit 0
fi
#
aws --profile ${AccountName} cloudformation package --template-file chaim_install_master.yaml --output-template chaim_root_template.yaml --s3-bucket ${BucketName}
