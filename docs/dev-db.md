# Chaim dev database setup

See (scripts/copy-chaim-to-dev.sh)[copy-chaim-to-dev.sh] for a script that
follows this procedure.


* prod account: secadmin-prod 499223386158 alias `sadmin`
* dev account: sredev 627886280200 alias `sdev`
* obtain chaim credentials for both accounts

```
cca account -D -r apu -d 4 -a sadmin secadmin-prod
cca account -r apu -d 4 -a sdev sredev
```

* Check that the prod KMS key `sre-chaim` is shared with the dev account

* Create a snapshot
```
snapshotname=chaim-db-$(date "+%Y%m%d")
encsnap=${snapshotname}-enc
prolog="aws --profile sadmin rds"

$prolog create-db-snapshot \
    --db-instance-identifier chaim-db \
    --db-snapshot-identifier $snapshotname
```

* wait for snapshot to become available

```
$prolog describe-db-snapshots \
    --db-snapshot-identifier $snapshotname | \
    jq '.DBSnapshots[].Status'
```

* re-encrypt the copy with the shared KMS key
```
$prolog copy-db-snapshot \
    --source-db-snapshot-identifier $snapshotname \
    --target-db-snapshot-identifier $encsnap \
    --kms-key-id alias/sre-chaim
```

* wait for the copy to become available
```
$prolog describe-db-snapshots \
    --db-snapshot-identifier $encsnap | \
    jq '.DBSnapshots[].Status'
```

* share the snapshot with sredev
```
$prolog modify-db-snapshot-attribute \
    --db-snapshot-identifier $encsnap \
    --attribute-name restore \
    --values-to-add '["627886280200"]'
```

* grab the ARN of the snapshot
```
snaparn=$($prolog describe-db-snapshots \
    --db-snapshot-identifier $encsnap | \
    jq -r '.DBSnapshots[].DBSnapshotArn')
```

* move to the `sredev` account
```
prolog="aws --profile sdev rds"
```

* copy from secadmin-prod to sredev, removing the dependency of the
  secadmin-prod KMS key
```
$prolog copy-db-snapshot \
    --source-db-snapshot-identifier $snaparn \
    --target-db-snapshot-identifier ${encsnap}-copy \
    --kms-key-id alias/aws/rds
```

* wait for the copy to become available
```
$prolog describe-db-snapshots \
    --db-snapshot-identifier ${encsnap}-copy | \
    jq '.DBSnapshots[].Status'
```

* it is easiest now to go to the RDS console to restore the database from
  the snapshot
* Once restored, though the users will still exist their grants will have
  mysteriously disappeared, so fire up a mysql console and
```
grant select on srechaim.* to 'chaimro'@'%';
grant select, update, insert, delete on srechaim.* to 'chaimrw'@'%';
```

You now have a chaim database running in sredev that is a copy of the
production database.


## Cross Account Roles Update
In the accounts that you will allow the dev infrastructure to access you
will need to alter the trust relationship on the chaim roles to also
include the dev account.

* Create the below json as `update-trust-policy.json`
```
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Principal": {"AWS": [
            "arn:aws:iam::499223386158:root",
            "arn:aws:iam::627886280200:root"
        ]},
        "Action": "sts:AssumeRole"
    }
}

```

* update the trust policy for the CrossAccountReadOnly and
  CrossAccountPowerUser roles in the target account(s)
```
for account in sdev; do
    for role in ReadOnly PowerUser; do
        aws --profile ${account} iam update-assume-role-policy \
            --role-name CrossAccount${role} \
            --policy-document file://update-trust-policy.json
    done
done
```


[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
