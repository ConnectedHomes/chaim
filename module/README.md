# Chaim
This module gives chaim functionality to your python scripts.

## usage
Chaim acts as a context manager for python scripts.  It obtains temporary credentials
for an AWS account under the alias 'tempname'.  These credentials are removed when
the context goes out of scope.

```
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
