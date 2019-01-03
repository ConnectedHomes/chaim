# Install Chaim

## AWS Configuration

The 'chaim account' is the central account that you wish to use for chaim to
run it.  It is this account that where the roles for all accounts are assumed
from.

### Permission Policies

The different parts of Chaim require certain permissions.  These are granted
via policies.  The files under the policies directory are provided as a guide
and grant the minimum permissions that chaim requires.  In all the files the
main chaim account is `111111111111` and any secondary account will be noted as
`222222222222`, `333333333333` ... etc if used.

see the [policy README](policies/README.md) for information.


### User

Chaim requires a 'machine user' IAM account to run as:

```
aws iam --create-user --user-name sre.chaim
```

### Encryption Key

All of Chaims parameters and secrets are held, encrypted, in the parameter
store. Create a KMS key to encrypt/decrypt them:

```
tags="TagKey=role,TagValue=encryptionkey"
tags="${tags},TagKey=owner,TagValue=SRE"
tags="${tags},TagKey=product,TagValue=chaim"
tags="${tags},TagKey=environment,TagValue=prod"
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

### SNS Topic
### roles
