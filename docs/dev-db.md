# Chaim dev database setup

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

* re-encrypt the copy with the shared kms key
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
  secadmin-prod kms key
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

* it is easiest now to go to the rds console to restore the database from
  the snapshot
* Once restored, though the users will still exist their grants will have
  mysteriously disappeared, so fire up a mysql console and
```
grant select on srechaim.* to 'chaimro'@'%';
grant select, update, insert, delete on srechaim.* to 'chaimrw'@'%';
```

You now have a chaim database running in sredev that is a copy of the
production database.

[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
