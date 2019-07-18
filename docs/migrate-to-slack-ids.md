# Migrate to Using Slack User Ids
The current implementation uses slack display names as the identifier. With
the migration to Cloud based Active Directory services the Slack login will
change those identifiers (I have no idea why, ask the Microsoft team).
Apparently the slack user ids will not change, however, so we need to
switch to using those as identifiers.

## Initial Steps
The following steps will be required initially.
1. Obtain a map of slack userids to slack display names
2. Update the `awsusers` table in the chaim db adding a `slackid` column
3. Add the slack userid to the `awsusers` table for the appropriate user.
4. Should a map of slack userids not be available then the alternative of
   inserting the slack userids into the `awsusers` table as they become
   available by usage (of the `/chaim` and `/initchaim` slack commands) will
   have to utilised.  This process will take 5 weeks, anyone on holiday
   will be missed - tread carefully.
5. Once we have all slack display names mapped to slack userids then the
   applications can be switched to using the slack userids rather than the
   display names as identifiers.
6. Testing of the new code will have to take place using the slack commands
   `/zzchaim-dev` and `/zzinitchaim-dev`.


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
