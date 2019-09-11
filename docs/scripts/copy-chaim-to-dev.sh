#!/bin/bash


cca account -D -r apu -d 4 -a sadmin secadmin-prod
cca account -r apu -d 4 -a sdev sredev

prodkey=alias/sre-chaim

snapshotname=chaim-db-$(date "+%Y%m%d")
encsnap=${snapshotname}-enc
prolog="aws --profile sadmin rds"

echo "Creating initial snapshot $snapshotname"
# Create a snapshot
$prolog create-db-snapshot \
    --db-instance-identifier chaim-db \
    --db-snapshot-identifier $snapshotname

echo
# wait for snapshot to become available
status=waiting
while [ ! "$status" = "available" ]; do
    printf ". "
    sleep 10
    status=$($prolog describe-db-snapshots \
    --db-snapshot-identifier $snapshotname | \
    jq -r '.DBSnapshots[].Status')
done
echo
echo "Snapshot $snapshotname created OK"
echo
echo "Encrypting with shared key"
echo

# re-encrypt the copy with the shared KMS key
$prolog copy-db-snapshot \
    --source-db-snapshot-identifier $snapshotname \
    --target-db-snapshot-identifier $encsnap \
    --kms-key-id $prodkey

# wait for the copy to become available
status=waiting
while [ ! "$status" = "available" ]; do
    printf ". "
    sleep 10
    status=$($prolog describe-db-snapshots \
        --db-snapshot-identifier $encsnap | \
        jq -r '.DBSnapshots[].Status')
done
echo
echo "Encrypted Snapshot $encsnap created OK"

# share the snapshot with sredev
echo "Sharing encrypted copy with 'sredev' account"
$prolog modify-db-snapshot-attribute \
    --db-snapshot-identifier $encsnap \
    --attribute-name restore \
    --values-to-add '["627886280200"]'

# grab the ARN of the snapshot
snaparn=$($prolog describe-db-snapshots \
    --db-snapshot-identifier $encsnap | \
    jq -r '.DBSnapshots[].DBSnapshotArn')

# move to the `sredev` account
prolog="aws --profile sdev rds"

echo "Copying snapshot to sredev account"
# copy from secadmin-prod to sredev, removing the dependency of the
# secadmin-prod KMS key
$prolog copy-db-snapshot \
    --source-db-snapshot-identifier $snaparn \
    --target-db-snapshot-identifier ${encsnap}-copy \
    --kms-key-id alias/aws/rds


# wait for the copy to become available
status=waiting
while [ ! "$status" = "available" ]; do
    printf ". "
    sleep 10
    status=$($prolog describe-db-snapshots \
        --db-snapshot-identifier ${encsnap}-copy | \
        jq -r '.DBSnapshots[].Status')
done
echo
echo "Encrypted Snapshot Copy ${encsnap}-copy created OK"
