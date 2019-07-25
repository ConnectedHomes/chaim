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

```
tags="${deftags},Key=role,Value=sns-topic"
tags="${tags},Key=Name,Value=chaim-entry-dev"

aws sns create-topic --name chaim-entry-dev --tags "${tags}" |tee $opdir/create-sns-topic.json
```
[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
