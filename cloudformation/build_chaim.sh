#!/bin/bash
#
if [ $# -ne 1 ]
then
  echo "Need an AWS account name to build chaim in"
  exit 0
fi
#
AccountName=$1
StackName='ian-test-chaim'
MyDir=${0%/*}
if [ ! -e ${MyDir}/chaim_policies.yaml ]
then
  echo "chaim_policies.yaml is missing from this directory"
  exit 0
fi
if [ ! -e ${MyDir}/chaim_policies_parameters_${AccountName}.json ]
then
  echo "chaim_policies_parameters_${AccountName}.json is missing from this directory"
  exit 0
fi
#
aws --profile ${AccountName} cloudformation create-stack --template-body file://chaim_policies.yaml --parameters file://chaim_policies_parameters_${AccountName}.json --stack-name ${StackName} --capabilities CAPABILITY_NAMED_IAM
