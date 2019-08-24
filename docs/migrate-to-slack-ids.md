# Migrate to Using Slack User Ids
The current implementation uses slack display names as the identifier. With
the migration to Cloud based Active Directory services the Slack login will
change those identifiers (I have no idea why, ask the Microsoft team).
Apparently the slack user ids will not change, however, so we need to
switch to using those as identifiers.

It has been discovered that Slack user ids are workspace specific,
therefore the workspace id will also have to be collected and utilised.

We will require a mapping table in the database of chaim user ids, slack
user ids and workspace id.  See the [slackmap-create.sql](slackmap-create.sql) in this
repo. The [o365-alter-awsusers-table.sql](o365-alter-awsusers-table.sql)
file is no longer required and has been removed.

1. Go to the admin page for slack: [manage
   members](img/slack-manage-members.png "manage members")
2. Download a CSV format file of all Slack Users:
   [download](img/slack-download-users.png "download user list")
3. Obtain the current chaim user list:
```
$ workon chaim-dev-manager
$ cdm start

$ muser=$(aws --profile sdev ssm get-parameter \
    --with-decryption --name /sre/chaim/dev/dbrouser | \
    jq -r '.Parameter.Value')
$ mpass=$(aws --profile sdev ssm get-parameter \
    --with-decryption --name /sre/chaim/dev/dbropass | \
    jq -r '.Parameter.Value')

$ chaimfn=~/tmp/chaim-users.tsv

$ mysql -h 127.0.0.1 -P 3306 -u ${muser} -p${mpass} srechaim  \
    -e "select id,name from awsusers" |tee $chaimfn
```
4. See [jira SRE-1102](https://jira.bgchtest.info/browse/SRE-1102) for a
   script to merge the user list from slack and the list of chaim users
   from above.  This script creates a `slackmap-inserts.sql` file that can
   be inserted thus:
```
$ muser=$(aws --profile sdev ssm get-parameter \
    --with-decryption --name /sre/chaim/dev/dbrwuser | \
    jq -r '.Parameter.Value')
$ mpass=$(aws --profile sdev ssm get-parameter \
    --with-decryption --name /sre/chaim/dev/dbrwpass | \
    jq -r '.Parameter.Value')

$ mysql -h 127.0.0.1 -P 3306 -u ${muser} -p${mpass} srechaim <slackmap-inserts.sql
```





## Code Changes.
It will be necessary to identify all places in the code that use the slack
display name and substitute routines that use the slack user id.

At first glance this should just be within the following files
`chalicelib/commandparse.py`
`chalicelib/permissions.py`
`lambda/chaim-entry/app.py`
`lambda/chaim-snsreq/chaim-snsreq.py`

There maybe others.

[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
