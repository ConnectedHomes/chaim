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
deftags="TagKey=owner,TagValue=SRE"
deftags="${deftags},TagKey=product,TagValue=chaim"
deftags="${deftags},TagKey=environment,TagValue=prod"
```

These will be used later when creating the infrastucture from the command line.

### Permission Policies

The different parts of Chaim require certain permissions.  These are granted
via policies.  The files under the policies directory are provided as a guide
and grant the minimum permissions that chaim requires.  In all the files the
main chaim account is `111111111111` and any secondary account will be noted as
`222222222222`, `333333333333` ... etc if used.

see the [policy README](policies/README.md) for information.

Create all those policies before attempting to create the Roles below.


### User

Chaim requires a 'machine user' IAM account to run as:

```
tags="${deftags},TagKey=role,TagValue=Chaim-Master-User"
tags="${tags},TagKey=Name,TagValue=sre.chaim"

aws iam --create-user --user-name sre.chaim --tags "${tags}"
```

### Encryption Key

All of Chaim's parameters and secrets are held, encrypted, in the parameter
store. Create a KMS key to encrypt/decrypt them:

```
tags="${deftags},TagKey=role,TagValue=encryptionkey"
tags="${tags},TagKey=Name,TagValue=sre-chaim"

desc="Encrypt secrets for the chaim application"

aws kms --create-key --policy file://policies/chaim-kms.json \
--description "${desc}" \
--tags "${tags}"
```

Record the KeyId of the created key and use it to create a key alias:

```
aws kms --create-alias --alias-name sre-chaim --target-key-id ${keyid}
```

The alias cannot be tagged.

### Role: chaim-lambda-rds

This is the role that most of the chaim application runs as.  Create the
policies first (see above).

Change the account number below in the `polarn` line to be the correct one.

```
tags="${deftags},TagKey=role,TagValue=chaim-role"
tags="${tags},TagKey=Name,TagValue=chaim-lambda-rds"

desc="chaim access to IAM, Parameter Store, Cognito and RDS"

polnames=(param-store-read sts-assume-role cognito-get-user-status)
polnames=(${polnames[@]} cognito-manage-user-pool chaim-publish-to-sns)

for poln in ${polnames[@]}; do
    polarn=arn:aws:iam::111111111111:policy/${poln}
    polarns=(${polarns[@]} ${polarn})
done

vpcexe=arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole


aws iam create-role --role-name chaim-lambda-rds \
--description "${desc}" \
--assume-role-policy-document file://policies/lambda-role-policy.json \
--tags "${tags}"

# give AWS time to update with the new Role
sleep 5

aws iam attach-role-policy --role-name chaim-lambda-rds --policy-arn ${vpcexe}

for polarn in ${polarns[@]}; do
    aws iam attach-role-policy --role-name chaim-lambda-rds --policy-arn ${polarn}
done
```

### Role: chaim-lambda-keyman

This role is used by the rotate-access-keys lambda to rotate Chaims long term
access keys on a cron schedule.

```
tags="${deftags},TagKey=role,TagValue=chaim-keyman"
tags="${tags},TagKey=Name,TagValue=chaim-lambda-keyman"

desc="Allows the chaim key manager lambda to access the parameter store \
read-write only certain keys and rotate access keys."

polnames=(chaim-manage-access-key chaim-paramstore-write)

for poln in ${polnames[@]}; do
    polarn=arn:aws:iam::111111111111:policy/${poln}
    polarns=(${polarns[@]} ${polarn})
done

lambdaexe=arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam create-role --role-name chaim-lambda-keyman \
--description "${desc}" \
--assume-role-policy-document file://policies/lambda-role-policy.json \
--tags "${tags}"

# give AWS time to update with the new Role
sleep 5

aws iam attach-role-policy --role-name chaim-lambda-keyman --policy-arn ${lambdaexe}

for polarn in ${polarns[@]}; do
    aws iam attach-role-policy --role-name chaim-lambda-keyman --policy-arn ${polarn}
done
```

### SNS Topic
