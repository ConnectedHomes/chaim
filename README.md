# Chaim
Chaim is the Centrica Hive AWS access and Identity Manager.

Chaim is a user service that enables easy access to Amazon Web Services.

Using Chaim a user can enter a simple command into Slack and receive a
clickable link that takes them to an already signed in AWS Console.  Chaim can
also be used to manage a users credentials file for use with the AWS CLI (and
boto like interfaces).

This is the repository for all of the chaim backend and api code.

## Testing Chaimlib
To run the full set of tests you will need your default aws credentials to be
for the `secadmin-prod` account.  You will also need to have the management
tunnel open (see [man-chaim](https://github.com/ConnectedHomes/man-chaim)).

You should also be in a virtual environment (`mkvenv ...` on a mac)
Install the requirements by `pip install -r test-requirements.txt` from within
the virtual enviroment.

### Testing
Run the tests by changing to the root of the repository and issuing:
```
pytest
```

Run the tests for each individual library file by
```
pytest tests/test_glue.py
```
(changing to the required file, obviously).

## Installation

see [install.md](install.md)

## Update

Update is via Makefiles. Additional Install instructions can be found
in the individual READMEs for each lambda (if any).

The Makefiles have the following targets:
1. `tags` - this will rebuild the tags files for each lambda
1. `depends` - this will rebuild the dependency chain for each lambda
1. `clean` - this will remove all but the latest zip file for each lambda
1. `dev` - this will increment the build number and rebuild the dev enviroment
         lambda if any of the files have changed.
1. `force` - this will increment the build number and rebuild the dev enviroment
   lambdas.
1. `prod` - this will build the prod environment lambda using the latest dev
   environment zip file. To ensure all lambdas are at the same version number
   issue a `make force` first to forcebly rebuild and update each one.

The Makefiles can be run individually or all together as a package.  To make
everything, issue `make <target>` from the root of the repository.  To make an
individual lambda cd to the corresponding directory and issue `make <target>`
