#!/bin/bash
#
if [ $# -ne 1 ]
then
  echo "Need an AWS account name to build chaim in"
  exit 0
fi
#
AccountName=$1
StackName='ian-test-chaim-module'
MyDir=${0%/*}
if [ ! -e ${MyDir}/chaim_kms.yaml ]
then
  echo "chaim_kms.yaml is missing from this directory"
  exit 0
fi
if [ ! -e ${MyDir}/chaim_parameters_kms.json ]
then
  echo "chaim_parameters_kms.json is missing from this directory"
  exit 0
fi
#
aws --profile ${AccountName} cloudformation create-stack --template-body file://chaim_kms.yaml --parameters file://chaim_parameters_kms.json --stack-name ${StackName} --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
