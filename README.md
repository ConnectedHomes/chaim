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
