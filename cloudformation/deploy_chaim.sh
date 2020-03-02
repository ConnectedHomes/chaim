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
if [ ! -e ${MyDir}/chaim_root_template.yaml ]
then
  echo "chaim_root_template.yaml is missing from this directory"
  exit 0
fi
if [ ! -e ${MyDir}/chaim_parameters_${AccountName}.properties ]
then
  echo "chaim_parameters_${AccountName}.properties is missing from this directory"
  exit 0
fi
#
aws --profile ${AccountName} cloudformation deploy --template-file chaim_root_template.yaml --parameter-override $(cat chaim_parameters_${AccountName}.properties) --stack-name ${StackName} --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
