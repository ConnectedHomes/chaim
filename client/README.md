# Chaim Click Utility
ccu is a re-imagining of the chaim cli using the click parameter parsing
python module.

<a name='contents'></a>
* [Install](#install)
* [Uninstall](#uninstall)
* [ccu commands](#ccucommands)
* [cca](#cca)
    * [cca examples](#ccaexamples)
* [ccm](#ccm)
    * [delete](#ccmdelete)
    * [gui](#ccmgui)
    * [gso](#ccmgso)
    * [init](#ccminit)
    * [list](#ccmlist)
    * [listall](#ccmlistall)
    * [listpark](#ccmlistpark)
    * [park](#ccmpark)
    * [renew](#ccmrenew)
    * [setautorenew](#ccmautorenew)
    * [unpark](#ccmunpark)
    * [url](#ccmurl)
    * [version](#ccmversion)

<a name='install'></a>
## Install
to install a development version (which will create a new branch tagged with
your name):
```
mkvirtualenv -p $(which python3) clickchaim
git pull
git checkout -b ${USER}-ccu-dev
git push -u origin ${USER}-ccu-dev
make dev
```
If make exits with an error, you probably need to upgrade your pip version
```
pip3 install --upgrade pip --user
```
and try `make dev` again.

to install a usable, no virtualenv needed, version, available from any prompt,
in the users own, local python package cache
```
git pull
make install
```
That command sequence can also be used to upgrade as well.

<a name='uninstall'></a>
## Uninstall
to uninstall the dev version, delete the virtualenvironment or
```
make uninstall
```
to keep the virtualenvironment intact, but without this package installed.

To uninstall the local, users package cache version
```
make uninstall
```
from outside any virtualenvironment.

<a name='ccucommands'></a>
## [ccu commands](#contents)
There are 2 basic commands (at the moment)
1. [cca](#cca) - generate credentials for an account
2. [ccm](#ccm) - manage credentials for accounts

<a name='cca'></a>
## [cca](#contents)
```
 $ cca --help
Usage: cca [OPTIONS] ACCOUNT

  Retrieve credentials for an account

Options:
  -r, --role TEXT         The role to assume for this account default: rro
  -d, --duration INTEGER  duration must be between 1-12 or 900-43,200 default
                          1
  -a, --alias TEXT        optional alias for the account name, to be used as
                          the profile name
  -D, --default           set this account to be the default account profile
                          to use
  -R, --region TEXT       optional region
  --help                  Show this message and exit.
```

<a name='ccaexamples'></a>
### [Examples](#contents)
Get Admin creds for the `secadmin-prod` account for 4 hours, give it a profile
name (alias) of `sadmin` and also make this the default account for the aws
cli.
```
cca -D -d 4 -r apu -a sadmin secadmin-prod
```

Get Power User creds for `is-prod` for 1 hour, with no alias
```
cca -r mpu is-prod
```

Get Read Only creds for 1 hour for `honeycomb-prod` with an alias of `hprod`
```
cca -a hrod honeycomb-prod
```

<a name='ccm'></a>
## [ccm](#contents)
```
$ ccm --help
Usage: ccm [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  gui    obtains a console session url and opens a...
  renew  Renews all account credentials

```

<a name='ccmsubcommands'></a>
### [ccm sub-commands](#contents)

<a name='ccmdelete'></a>
#### [delete](#contents)
Delete credentials for the named account(s)

<a name='ccmgui'></a>
#### [gui](#contents)
This command generates a console session url and opens a browser window to it.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.

<a name='ccmgso'></a>
#### [gso](#contents)
This command generates a console session url, attempts to logout of any current
session and opens a browser window to the url.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.

<a name='ccminit'></a>
#### [init](#contents)
Initialises the application with a usertoken obtained from slack.  Either
supply the base64 encoded info from slack as a parameter, or use the command
bare to be asked the pertinent questions.
```
ccm init YXBpPTh4eHNDczJmV4cGly...JlZ2lvbj1ldS13ZXN0LTE=
ccu has been re-initialised.
Your token will expire in 29 days, 21 hours, 19 minutes and 52 seconds.
```
or
```
ccm init
api (8xxssu8fs7):
username (chris.allison):
usertoken: ad2f05ed-78d7-xxxx-DDDD-8d90c64f9473
tokenexpires: 1536139015
stage (prod):
region (eu-west-1):
ccu has been re-initialised.
Your token will expire in 29 days, 21 hours, 18 minutes and 58 seconds.
```

<a name='ccmlist'></a>
#### [list](#contents)
Current list of accounts that are managed by ccu and their expiry times.
This also shows which is the default account and the percentage of time left.

<a name='ccmlistall'></a>
#### [listall](#contents)
Full list of all available accounts.

<a name='ccmlistpark'></a>
#### [listpark](#contents)
List accounts that have been parked.
```
 $ ccm listpark
hbetaus
hprodus
hprod
hbeta
hdev7
```


<a name='ccmpark'></a>
#### [park](#contents)
Remove an account from credentials and park it and its definition for later
use.
```
$ ccm park extbackup
extbackup account has been parked
```

<a name='ccmrenew'></a>
#### [renew](#contents)
This will renew all managed accounts.
```
$ ccm renew
ignoring awsbilling as it is not managed by ccu
account: secadmin-prod, alias: secadmin-prod, role: apu, duration: 4
Updated section secadmin-prod with new keys
updated default account
retrieval took 5 seconds.
account: chsre-dev, alias: chsre-dev, role: apu, duration: 4
Updated section chsre-dev with new keys
retrieval took 6 seconds.
```

<a name='ccmautorenew'></a>
#### [setautorenew](#contents)
Sets the percentage of time remaining before the account is auto-renewed when
requesting a url.
```
 $ ccm setautorenew 50
Console time will renew at 50% of session time
```

<a name='ccmunpark'></a>
#### [unpark](#contents)
Re-enable an account and automatically renew it's session so that it is
available for immediate use.
```
 $ ccm unpark hdev7
account: honeycomb-dev7, alias: hdev7, role: mpu, duration: 1
Updated section honeycomb-dev7 with new keys
retrieval took 7 seconds.
```

<a name='ccmurl'></a>
#### [url](#contents)
This command generates a console session url and copies it to the clipboard.
If the original session is less than the auto-renew session percentage the
account will be automatically renewed first.


<a name='ccmversion'></a>
#### [version](#contents)
Show the current version of this application
