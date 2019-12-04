# Centrica Chaim AWS Accounts CLI
This is the code for the command line utility `cca`.

cca is a re-imagining of the chaim cli using the click parameter parsing
python module.

<a name='version></a>
### Changelog
v2.5.0 Display role and region when listing managed accounts

v2.4.0 Allow receiving and passing the Slack Workspace Id in the chaim
credentials requests.

<a name='contents'></a>
* [Install](#install)
    * [Linux](#linux)
    * [Mac OSX](#macosx)
* [Upgrade](#upgrade)
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
    * [unpark](#ccaunpark)
    * [url](#ccaurl)
    * [version](#ccaversion)

<a name='install'></a>
## [Install](#contents)
The chaim-cli is a python 3 application. It is recommended to install into your
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
pip3 install chaim-cli --upgrade --user --no-cache-dir
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
### [Mac OSX](#contents)
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
pip install chaim-cli --upgrade --user --no-cache-dir
```

#### Update PATH
Once installed you will want to add `$HOME/Library/.Python/3.7/bin` to your path, if it
isn't already there (adjust the version to suit your circumstances):
```
echo 'export PATH=${HOME}/Library/Python/3.7/bin:${PATH}' >>${HOME}/.bashrc
```

#### Testing
To check that all went well:
```
cca version
```
Should give you the current version number of the chaim-cli.

<a name='upgrade'></a>
## [Upgrade](#contents)
```
pip3 install chaim-cli --upgrade --user
```

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

  Retrieve credentials for ACCOUNT account

Options:
  -r, --role TEXT         optional the role to assume for this account
                          default: rro
  -d, --duration INTEGER  optional duration must be between 1-12 or 900-43,200
                          default 1
  -a, --alias TEXT        optional alias for the account name, to be used as
                          the profile name
  -D, --default           optional set this account to be the default account
                          profile to use
  -R, --region TEXT       optional region
  -T, --terrible          Add support for Terraform/Ansible to the credentials
                          file
  --help                  Show this message and exit.
```
The `-T|--terrible` switch copies the `aws_session_token` key to the `aws_security_token` key.
This ensures that products such as Ansible and Terraform which still use the `aws_security_token`
will continue to work.

<a name='ccadelete'></a>
#### [delete](#contents)
Delete credentials for the named account(s).

<a name='ccagui'></a>
#### [gui](#contents)
This command generates a console session url and opens a browser window to it.
The credentials will be automatically renewed first.

<a name='ccagso'></a>
#### [gso](#contents)
This command generates a console session url, attempts to logout of any current
session, and opens a browser window to the url.
The credentials will be automatically renewed first.

Note: There doesn't seem to be any way to access the browser tab with AWS
running in it, so this process first opens a new tab to issue the logout
command, then a 2nd new tab to log you into the new account.  This will leave
you with 2 extra tabs, sorry.

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
Current list of accounts that are managed by cca, the role and region and their expiry times.
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
The credentials will be automatically renewed first.


<a name='ccaversion'></a>
#### [version](#contents)
Show the current version of this application.

[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
