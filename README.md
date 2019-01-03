# Chaim
this is the repository for all of the chaim backend and api code.

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

## Installing
Installation is via Makefiles. They have the following targets
1. `tags` - this will rebuild the tags files for each lambda
1. `clean` - this will remove all but the latest zip file for each lambda
1. `dev` - this will increment the build number and rebuild the dev enviroment
         lambda if any of the files have changed.
1. `force` - this will increment the build number and rebuild the dev enviroment
   lambdas.
1. `prod` - this will build the prod environment lambda using the latest dev
   environment zip file (i.e. use `make force` first to ensure all lambdas are
   showing the same version number).

The Makefiles can be run individually or all together as a package.  To make
everything, issue `make <target>` from the root of the repository.  To make an
individual lambda cd to the corresponding directory and issue `make <target>`
