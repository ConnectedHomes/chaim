# Centrica Chaim AWS Accounts CLI
This is the code for the command line utility `cca`.

cca is a re-imagining of the chaim cli using the click parameter parsing
python module.

<a name='contents'></a>
* [Install](#install)
    * [Linux](#linux)
    * [Mac OSx](#macosx)
* [cca](#cca)
* [cca sub-commands](#ccasubcommands)
    * [account](#ccaaccount)
    * [delete](#ccadelete)
    * [gui](#ccagui)
    * [gso](#ccagso)
    * [init](#ccainit)
    * [list](#ccalist)
    * [listall](#ccalistall)
    * [listpark](#ccalistpark)
    * [park](#ccapark)
    * [renew](#ccarenew)
    * [setautorenew](#ccaautorenew)
    * [unpark](#ccaunpark)
    * [url](#ccaurl)
    * [version](#ccaversion)

<a name='install'></a>
## [Install](#contents)
The chaim-cli is a python 3 application. I recommend installing into your
local, users, python packages using pip.  If this is your first local python
package then you will need to adjust your path so that the shell can find it.
```
echo 'export PATH=${HOME}/.local/bin:${PATH}' >>${HOME}/.bashrc
```

<a name='linux'></a>
### [Linux](#contents)
These instructions are for ubuntu and it's derivatives.  For other
distributions the process is similiar, though probably with different package
names.  You will need to have a version of python3 installed and a pip program
that is python3 aware.

#### Install python3
For ubuntu pre 18.04 you will need to install python3 and it's associated pip
application.  The easiest way to do this is:

```
sudo apt install python3-pip
```
which will pull in everything required.

#### Install cca
To install the chaim-cli:
```
pip3 install chaim-cli --user
```

#### Update PATH
Once installed you will want to add `$HOME/.local/bin` to your path, if it
isn't already there:
```
echo 'export PATH=${HOME}/.local/bin:${PATH}' >>${HOME}/.bashrc
```

#### Testing
To check that all went well:
```
cca version
```
Should give you the current version number of the chaim-cli.

<a name='macosx'></a>
### [Mac OSx](#contents)
#### Install python3
Recently the folks that manage homebrew changed the default python, which
conflicts with the python supplied by the OS.  See this home brew
[discussion](https://discourse.brew.sh/t/brew-install-python3-fails/1756/8).
So, to get python3 (and keep python2) you now need to do:
```
brew upgrade python
brew install python2
```
which will install python3 and the latest released version of python2.

#### Install cca
To install the chaim-cli:
```
pip install chaim-cli --user
```

#### Update PATH
Once installed you will want to add `$HOME/.local/bin` to your path, if it
isn't already there:
```
echo 'export PATH=${HOME}/.local/bin:${PATH}' >>${HOME}/.bashrc
```

#### Testing
To check that all went well:
```
cca version
```
Should give you the current version number of the chaim-cli.

<a name='cca'></a>
## [cca](#contents)

```
$ cca --help
Usage: cca [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  account       Retrieve credentials for an account
  delete        delete an accounts credentials
  gso           obtains a console session url, logs out of...
  gui           obtains a console session url and opens a...
  init          Initialises the application for use with...
  list          list all registered accounts and their expiry...
  listall       list all accounts available to chaim
  listpark      list of parked accounts
  park          removes account from credentials and parks it...
  renew         Renews all account credentials
  setautorenew  sets the percentage of time remaining before...
  unpark        returns an account from parking to...
  url           obtains a console session url and copies it...
  version
```

<a name='ccasubcommands'></a>
### [cca sub-commands](#contents)

<a name='ccaaccount'></a>
#### [account](#contents)
```
$ cca account --help
Usage: cca account [OPTIONS] ACCOUNT

  Retrieve credentials for an account

Options:
  -r, --role TEXT         optional the role to assume for this account default: rro
  -d, --duration INTEGER  optional duration must be between 1-12 or 900-43,200 default 1
  -a, --alias TEXT        optional alias for the account name, to be used as
                          the profile name
  -D, --default           set this account to be the default account profile
                          to use
  -R, --region TEXT       optional region
  --help                  Show this message and exit.

```

<a name='ccadelete'></a>
#### [delete](#contents)
Delete credentials for the named account(s).

<a name='ccagui'></a>
#### [gui](#contents)
This command generates a console session url and opens a browser window to it.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.

<a name='ccagso'></a>
#### [gso](#contents)
This command generates a console session url, attempts to logout of any current
session, and opens a browser window to the url.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.

<a name='ccainit'></a>
#### [init](#contents)
Initialises the application with a user token obtained from Slack.  Either
supply the base64 encoded info from Slack as a parameter, or use the command
bare to be asked the pertinent questions.
```
cca init YXBpPTh4eHNDczJmV4cGly...JlZ2lvbj1ldS13ZXN0LTE=
cca has been re-initialised.
Your token will expire in 29 days, 21 hours, 19 minutes and 52 seconds.
```
or
```
cca init
api (8xxssu8fs7):
username (chris.allison):
usertoken: ad2f05ed-78d7-xxxx-DDDD-8d90c64f9473
tokenexpires: 1536139015
stage (prod):
region (eu-west-1):
cca has been re-initialised.
Your token will expire in 29 days, 21 hours, 18 minutes and 58 seconds.
```

<a name='ccalist'></a>
#### [list](#contents)
Current list of accounts that are managed by cca and their expiry times.
This also shows which is the default account, and the percentage of time left.

<a name='ccalistall'></a>
#### [listall](#contents)
Full list of all available accounts.

<a name='ccalistpark'></a>
#### [listpark](#contents)
List accounts that have been parked.
```
$ cca listpark
hbetaus
hprodus
hprod
hbeta
hdev7
```

<a name='ccapark'></a>
#### [park](#contents)
Remove an account from credentials and park it and its definition for later
use.
```
$ cca park extbackup
extbackup account has been parked
```

<a name='ccarenew'></a>
#### [renew](#contents)
This will renew all managed accounts.
```
$ cca renew
ignoring awsbilling as it is not managed by cca
account: secadmin-prod, alias: secadmin-prod, role: apu, duration: 4
Updated section secadmin-prod with new keys
updated default account
retrieval took 5 seconds.
account: chsre-dev, alias: chsre-dev, role: apu, duration: 4
Updated section chsre-dev with new keys
retrieval took 6 seconds.
```

<a name='ccaautorenew'></a>
#### [setautorenew](#contents)
Sets the percentage of time remaining before the account is auto-renewed when
requesting a url. We recommend leaving this at the default of 90%.
```
$ cca setautorenew 97
Console time will renew at 97% of session time
```

<a name='ccaunpark'></a>
#### [unpark](#contents)
Re-enable an account and automatically renew its session so that it is
available for immediate use.
```
$ cca unpark hdev7
account: honeycomb-dev7, alias: hdev7, role: mpu, duration: 1
Updated section honeycomb-dev7 with new keys
retrieval took 7 seconds.
```

<a name='ccaurl'></a>
#### [url](#contents)
This command generates a console session url and copies it to the clipboard.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.


<a name='ccaversion'></a>
#### [version](#contents)
Show the current version of this application.
