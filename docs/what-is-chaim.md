# Chaim demo
Authentication is via AD backed Slack

Chaim has 4 parts
1. authorisation database
2. cross-account roles in the target accounts
2. Assumed role constructor
3. Federated login constructor

## Authorisation Database

1. cognito db callback for simple enabled/disabled switch (in the absense of
any sane connection to AD)

2. A single table mapping userids, roleids and accountids - a single call
into the database to answer the question "is this person allowed to access
this account at this role".


## Cross-Account Roles

The required roles with attached permission policies are set up in each
target account. The Roles all have the 'chaim' account as trustee.


## Assumed Role Constructor

The process of assuming a role in AWS actually generates short-term Access
Keys along with a Session Token.  Since late 2016 most of commandline tools
can use this temporary access key and session token.

It is a simple leap then to pass these temporary credentials back to the
user for their day-to-day use.  The well-known AWS Credentials file can be
used to store these keys, and it is trivial to regenerate them as required.


## Federated Login Constructor

Using the AWS Federation Service, passing in the temporary Key ID and
Session Token, a logged-in URL can be constructed, which, when returned to
the user will be usable from any modern Internet Browser. No further
authentication will be required.


