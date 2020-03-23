#!/bin/bash

profile=awsbilling
acctn=324919260230

ln=chaim-account-sync-send
fns=(${ln}.py organisations.py)
for fn in ${fns[@]} requirements.txt; do
    if [ ! -r $fn ]; then
        echo "File $fn not found."
        echo "Script must be run from the chaim-account-sync-send directory"
        exit 1
    fi
done

rm -rf build
pip3 install -r requirements.txt -t build

cd build

# these are already present in any lambda
# no need to package them up (if you do the lambda
# code will be too 'big' to display
rm -rf bin boto3* botocore* dateutil docutils* \
    jmespath* __pycache__ python_dateutil* \
    s3transfer* six* urllib3*

for fn in ${fns[@]}; do
    cp ../$fn ./
done

alfn=${ln}.py
majorv=$(sed -n '/^majorv/s/^majorv = \([0-9]\+\).*$/\1/p' ${alfn})
minorv=$(sed -n '/^minorv/s/^minorv = \([0-9]\+\).*$/\1/p' ${alfn})
buildv=$(sed -n '/^buildv/s/^buildv = \([0-9]\+\).*$/\1/p' ${alfn})
version="${majorv}.${minorv}.${buildv}"

echo "Version: $version"

pkgd=../package
mkdir -p ${pkgd}
zipfn="${pkgd}/${ln}-${version}.zip"

zip -r ${zipfn} *

echo "Built ${zipfn}"
aws --profile ${profile} s3 cp ${zipfn} s3://centricasecurity-${acctn}
