# chaim account sync send
Obtains the list of accounts from the organisation and sends them
via SNS to the secadmin-prod account.

## Testing

```
$ AWS_PROFILE=awsbilling poetry run python chaim-account-sync-send.py

23/03/2020 10:28:06 [INFO ]  Chaim Account Sync Send version: 1.0.0
23/03/2020 10:28:09 [INFO ]  119 active accounts
23/03/2020 10:28:09 [INFO ]  3 inactive accounts
```

## Install
Use the build-send.sh script to build the lambda package and copy it
to the S3 bucket in the Billings account.

```
$ cd /home/chris/src/chaim/lambda/chaim-account-sync-send
$ ./build-send.sh
```

Use the cfn tool https://pypi.org/project/cfntool/ to install/update
the lambda function.

```
$ cfn -P awsbilling -I -n chaim-account-sync-send -p chaim -a "Connected Homes" \
-m LambdaVersion=1.0.0,EnvEnv=prod -t cloudformation/chaim-account-sync-send-CF.yaml
```
