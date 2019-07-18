# chaim-rotate-access-keys
Function to periodically rotate the long term access keys that chaim uses to
assume roles.

## Update
```
make <env>
```
where `<env>` is one of `dev`, `force` or `prod`. `dev` and `force` both update
the `dev` environment.

## Install
Create a user for chaim to run as:
```
aws iam --create-user --user-name sre.chaim
```

Chaim requires certain permissions to operate successfully. These are granted
by policies.

### Policies



[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
