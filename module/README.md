# Chaim
This module gives chaim functionality to your python scripts.

## usage
Chaim acts as a context manager for python scripts.  It obtains temporary credentials
for an AWS account under the alias 'tempname'.  These credentials are removed when
the context goes out of scope.

```
from chaim.chaimmodule import Chaim

with Chaim("sredev", "mpu", 1) as success:
    # if success is True we successfully obtained credentials
    if success:
        # we are 'in context' so the credentials are valid
        ses = boto3.session.Session(profile_name="tempname")
        client = ses.client("s3")
        buckets = client.list_buckets()

# script continues but we are now 'out of context' so the credentials are no longer
# valid and have been deleted.
print("all done")
```

Chaim can also act as an ordinary python class facilitating access to chaim accounts.  Each object
only works with one AWS account.  You should set the `tempname` class constructor variable to a
unique value if you use more than one instance at once.

You will need to call `Chaim.requestKeys()` to actually get keys for the account.

It should be thread safe as there is thread locking code in the ini file write routine.

```
from chaim.chaimmodule import Chaim

ch = Chaim("sredev", "rro", 1, tempname="uniquename12")
success = ch.requestKeys()
...
# when program ends or object is destroyed Chaim.deleteAccount() is automatically called
# which will delete the account information from the ini file
del(ch)
```

Chaim can be quite 'chatty' and defaults to logging output to stderr.  There are 3
levels of verboseness:

  `0`: only show errors

  `1`: show progress

 `>1`: debug messages

verbose defaults to `0`

## API
### Parameters
Parameters to set up the Chaim Object

  `account` - the full account name to obtain credentials for.

  `role` - the chaim role to access the account as.

  `duration` - integer between 1 and 12 for number of hours to hold the credentials for.
             defaults to 1 hour.

  `region` - defaults to 'eu-west-1'.

  `tempname` - the alias for the account - defaults to 'tempname'.

  `terrible` - set to True for Ansible/Terraform support - defaults to False.

  `verbose` - set loglevel, defaults to WARN, 1 = INFO, >1 = DEBUG

  `logfile` - log output to a seperate file, defaults to NONE.

### Exceptions
Chaim has 2 unique exceptions

  `UmanagedAccount`

  `NoUrl`

Neither of these should be thrown when using as a context manager.

### Callable Methods
None of these are intended for basic, context manager, usage, this list is provided
for completeness.  To use these the Chaim object must be setup first.

These Functions have been written to ease future expansion of this module.

#### `getDefaultSection()`
returns the default section from the credentials file

#### `getDefaultAccount()`
returns the default account name as set in the credentials file

#### `getEndpoint()`
returns the url to access the chaim api gateway

#### `renewSection(section)`
requests updated credentails for the account named in `section`

#### `requestKeys()`
Obtains credentials from chaim.  Takes no parameters

#### `storeKeys(text)`
Stores the keys contained in `text` into the credential file format.

`text` should be the returned text from a requests object. It should be convertable
into json and then into a python dictionary.

#### `myAccountList()`
Returns a list of tuples describing your current chaim accounts

`[(account, expire timestamp, expire string, default account),(...)]`

#### `displayMyList()`
Logs the current chaim credentials you hold, along with their expiration times.

#### `requestList()`
Returns a list of tuples of all account ids and account names that chaim knows about

`[(account number, account name),(...)]`

#### `deleteAccount(account)`
Deletes the account credentials `account` from the credentials file

#### `parkAccount(account)`
Removes the `account` definition from the credentials file and stores it for later use
in the chaim-parked accounts file

#### `unparkAccount(account)`
Removes the `account` definition from the chaim-parked accounts file, adds it to the
credentials file and renews the credentials for it.

#### `listParkAccounts()`
Returns a list of parked account aliases.

`["cdev","hprod",...]`
