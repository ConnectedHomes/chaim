# Install Chaim

## AWS Configuration

The 'chaim account' is the central account that you wish to use for chaim to
run in.  It is this account that assumable roles in all accounts are assumed
from.

Obtain credentials for this account and store them in `~/.aws/credentials`.

Issue `export AWS_PROFILE=<chaim account profile name>` in your shell.

### Tagging

In your shell create a default set of tags:

```
deftags="Key=owner,Value=SRE"
deftags="${deftags},Key=product,Value=chaim"
deftags="${deftags},Key=environment,Value=prod"
```

These will be used later when creating the infrastructure from the command line.

And a directory for output

```
accountname=sredev
opdir=~/tmp/chaim-${accountname}-output
mkdir -p ${opdir}
```


### Permission Policies

The different parts of Chaim require certain permissions.  These are granted
via policies.  The files under the policies directory are provided as a guide
and grant the minimum permissions that chaim requires.  In all the files the
main chaim account is `111111111111` and any secondary account will be noted as
`222222222222`, `333333333333` ... etc if used.

see the [policy README](policies/README.md) for information.

Create the policy set as described in that document, but don't create the
policies marked as special, as they are created when creating the
functions.


### User

Chaim requires a 'machine user' IAM account to run as:

```
tags="${deftags},Key=role,Value=Chaim-Master-User"
tags="${tags},Key=Name,Value=sre.chaim"

aws iam create-user --user-name sre.chaim --tags "${tags}" | tee $opdir/create-user.json
```

### Role: chaim-lambda-rds

This is the role that most of the chaim application runs as.  Create the
policies first (see above).

Change the account number below in the `polarn` line to be the correct one.

```
tags="${deftags},Key=role,Value=chaim-role"
tags="${tags},Key=Name,Value=chaim-lambda-rds"

desc="chaim access to IAM, Parameter Store, Cognito and RDS"

polnames=(param-store-read sts-assume-role cognito-get-user-status)
polnames=(${polnames[@]} cognito-manage-user-pool chaim-publish-to-sns)

for poln in ${polnames[@]}; do
    polarn=arn:aws:iam::${acctnum}:policy/${poln}
    polarns=(${polarns[@]} ${polarn})
done

vpcexe=arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole


aws iam create-role --role-name chaim-lambda-rds \
--description "${desc}" \
--assume-role-policy-document file://policies/lambda-role-policy.json \
--tags "${tags}" |tee $opdir/create-role.json

# give AWS time to update with the new Role
sleep 5

aws iam attach-role-policy --role-name chaim-lambda-rds \
--policy-arn ${vpcexe} |tee $opdir/attach-policies.json

for polarn in ${polarns[@]}; do
    aws iam attach-role-policy --role-name chaim-lambda-rds \
    --policy-arn ${polarn} |tee -a $opdir/attach-policies.json
done
```

### Encryption Key

All of Chaim's parameters and secrets are held, encrypted, in the parameter
store. Create a KMS key to encrypt/decrypt them:

```
tags="${deftags},Key=role,Value=encryptionkey"
tags="${tags},Key=Name,Value=sre-chaim"

# for some reason known only to the AWS CLI devs the tags for
# the create-key command have to be 'TagKey=keyname,TagValue=value'
ttags="$(echo $tags |sed 's/Key/TagKey/g; s/Value/TagValue/g')"

desc="Encrypt secrets for the chaim application"

aws kms create-key --policy file://policies/${accountname}/chaim-kms.json \
--description "${desc}" \
--tags "${ttags}" |tee $opdir/create-kms-key.json
```

Record the KeyId of the created key and use it to create a key alias:

```
keyid=0e3f5f92-XXXX-ZZZZ-YYYY-1f5xxxx33d05
aws kms create-alias --alias-name alias/sre-chaim \
--target-key-id ${keyid} |tee $opdir/create-key-alias.json
```

The alias cannot be tagged.

### Role: chaim-lambda-keyman

This role is used by the rotate-access-keys lambda to rotate Chaims long term
access keys on a cron schedule.

```
tags="${deftags},Key=role,Value=chaim-keyman"
tags="${tags},Key=Name,Value=chaim-lambda-keyman"

desc="Allows the chaim key manager lambda to access the parameter store \
read-write only certain keys and rotate access keys."

polnames=(chaim-manage-access-key chaim-paramstore-write)

for poln in ${polnames[@]}; do
    polarn=arn:aws:iam::${acctnum}:policy/${poln}
    polarns=(${polarns[@]} ${polarn})
done

lambdaexe=arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam create-role --role-name chaim-lambda-keyman \
--description "${desc}" \
--assume-role-policy-document file://policies/lambda-role-policy.json \
--tags "${tags}" |tee $opdir/create-rotate-role.json

# give AWS time to update with the new Role
sleep 5

aws iam attach-role-policy --role-name chaim-lambda-keyman --policy-arn ${lambdaexe} |tee -a $opdir/attach-policies.json

for polarn in ${polarns[@]}; do
    aws iam attach-role-policy --role-name chaim-lambda-keyman --policy-arn ${polarn} |tee -a $opdir/attach-policies.json
done
```

### SNS Topic

Create an SNS topic, record the ARN for later use.

```
tags="${deftags},Key=role,Value=sns-topic"
tags="${tags},Key=Name,Value=chaim-entry-dev"

aws sns create-topic --name chaim-entry-dev --tags "${tags}" |tee $opdir/create-sns-topic.json
```

## Infrastructure

### VPC

Create a VPC, 2 subnets, one public, one private, and a NAT Gateway

```
tags="${deftags},Key=role,Value=VPC"
tags="${tags},Key=Name,Value=chaim-db-network"

aws ec2 create-vpc --cidr-block 10.190.0.0/16 |tee $opdir/create-vpc.json
vpcid=$(jq -r '.Vpc.VpcId' $opdir/create-vpc.json)
# for some unknown reason this only sets the last tag
#  aws ec2 create-tags --resources ${vpcid} --tags "${tags}"
# so create them individually
aws ec2 create-tags --resources ${vpcid} --tags Key=role,Value=VPC
aws ec2 create-tags --resources ${vpcid} --tags Key=owner,Value=SRE
aws ec2 create-tags --resources ${vpcid} --tags Key=environment,Value=dev
aws ec2 create-tags --resources ${vpcid} --tags Key=product,Value=chaim

# subnets (create one in AZc as well for prod)
azs=(a b c)
for i in 0 1 2; do
    aws ec2 create-subnet --vpc-id ${vpcid} \
    --cidr-block 10.190.${i}.0/24 --availability-zone eu-west-1${azs[$i]} \
    |tee $opdir/create-subnets-${azs[$i]}.json
    subnetid=$(jq -r '.Subnet.SubnetId' $opdir/create-subnets-${azs[$i]}.json)
    if [ $1 -eq 0 ]; then
        subneta=$subnetid
    fi
    echo $subnetid
    aws ec2 create-tags --resources ${subnetid} --tags Key=role,Value=subnet
    aws ec2 create-tags --resources ${subnetid} --tags Key=owner,Value=SRE
    aws ec2 create-tags --resources ${subnetid} --tags Key=environment,Value=dev
    aws ec2 create-tags --resources ${subnetid} --tags Key=product,Value=chaim
    aws ec2 create-tags --resources ${subnetid} --tags Key=Name,Value=chaim-subnet-${azs[$i]}
done

# create an elastic IP for the NAT GW
allocid=$(aws ec2 allocate-address --domain vpc |jq -r '.AllocationId')

# create the NAT GW
aws ec2 create-nat-gateway --allocation-id $allocid --subnet-id $subneta

# create an internet gateway
aws ec2 create-internet-gateway |tee $opdir/create-igw.json
igwid=$(jq -r '.InternetGateway.InternetGatewayId' $opdir/create-igw.json)
aws ec2 attach-internet-gateway --internet-gateway-id $igwid --vpc-id $vpcid |tee $opdir/attach-igw.json

```
Now you have a VPC, 2 (or 3) subnets, an Internet Gateway and a NAT
Gateway.  It is easiest to tie them all together using the console.

* go to the VPC console and select Subnets.
* select the `chaim-db-network-a` subnet
* select the Route Table tab and click the link to the route table
* select the Routes tab
* select Edit Routes
* select Add Route
* in the destination box type `0.0.0.0/0`
* select Internet Gateway in the target box, and from the list select the
  new one you created above
* select Route Tables from the left hand menu
* select Create route table
* name it `chaim-db-network-private`
* select the correct VPC
* select the route table you just created
* edit the routes to add a route via the NAT GW
* select Subnets from the left hand menu again
* select `chaim-db-network-b` subnet
* select Route Table tab
* edit the route table association and change it to the route table you
  just created.

You now have a Public subnet (chaim-db-network-a) and 1 or 2 Private
subnets (chaim-db-network-b/c)


## Database and Security Group

### Security Group

Create a security group for database access

```
grpname=chaim-db-access-sg
tags="${deftags},Key=role,Value=security-group"
tags="${tags},Key=Name,Value=${grpname}"

desc="Security group for access to the chaim database"

aws ec2 create-security-group --description "${desc}" \
--group-name ${grpname} --vpc-id ${vpcid} |tee $opdir/create-db-sg.json

sgid=$(jq -r '.GroupId' $opdir/create-db-sg.json)
echo $sgid
aws ec2 create-tags --resources ${sgid} --tags Key=role,Value=security-group
aws ec2 create-tags --resources ${sgid} --tags Key=owner,Value=SRE
aws ec2 create-tags --resources ${sgid} --tags Key=environment,Value=dev
aws ec2 create-tags --resources ${sgid} --tags Key=product,Value=chaim
aws ec2 create-tags --resources ${sgid} --tags Key=Name,Value=${grpname}
```

### Database

* At the RDS console, select Create Database
* Select MariaDB
* Select Dev/Test as the use case
* Select the latest version of MariaDB
* Select db.t3.micro as the instance size
* Leave the other options as default
* Scroll down to Settings
* DB Instance Identifier: `chaim-db-dev`
* Create a Master Password and store it in the parameter store:

```
aws ssm put-parameter --type SecureString --key-id alias/sre-chaim \
--name /sre/chaim/dev/db-master-password --value 'password' \
--description "the master password for the chaim-db-dev instance"

aws ssm put-parameter --type SecureString --key-id alias/sre-chaim \
--description "the master username for the chaim-db-dev instance" \
--name /sre/chaim/dev/db-master-user --value 'master-user-name'
```

* Click Next
* Select the `chaim-db-network` VPC
* Set AZ to be `eu-west-1b`
* Set the default db name to be `srechaim`
* Set the backup retention period to be 0 days
* Select the 4 log exports
* Select Create Database






[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
