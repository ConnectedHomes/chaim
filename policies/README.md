# Chaim Permission Policies

The different parts of Chaim require certain permissions.  These are granted
via policies.  The files under the policies directory are provided as a guide
and grant the minimum permissions that chaim requires.  In all the files the
main chaim account is `111111111111` and any secondary account will be noted as
`222222222222`, `333333333333` ... etc if used.

## Files

The policy files will require editing of the account numbers (see above).

### chaim-kms

[chaim-kms.json](chaim-kms.json) is used for the encryption key in KMS

### chaim-manage-access-key

[chaim-manage-access-key.json](chaim-manage-access-key.json) is used to allow
chaim to manage it's long term credentials, so they get rotated regularly.

### chaim-cognito-manage-user.json

[chaim-cognito-manage-user.json](chaim-cognito-manage-user.json) is used by
chaim to manage the users in the cognito db.

### chaim-publish-to-sns.json

[chaim-publish-to-sns.json](chaim-publish-to-sns.json) allows chaim to publish
to various SNS topics.  This is a generic policy that can be used by more than
chaim (as can be seen) to allow a lambda to publish to SNS. It should be edited
as required.

### chaim-paramstore-write.json

[chaim-paramstore-write.json](chaim-paramstore-write.json) is used by the chaim
key-rotation lambda to store the new long term credentials in the parameter
store.

### cognito-get-user-status.json

[cognito-get-user-status.json](cognito-get-user-status.json) is used by chaim
to ascertain the state of the `Enabled` switch for the chaim username.

### cognito-manage-user-pool.json

[cognito-manage-user-pool.json](cognito-manage-user-pool.json) used by the
chaim manager to manage users in the cognito user pool.

### param-store-read.json

[param-store-read.json](param-store-read.json) is used by chaim to read the
encrypted parameters from the Parameter Store.

### sts-assume-role.json

[sts-assume-role.json](sts-assume-role.json) allows the chaim user to assume
the requested role.
