# Development Install
To install a development version (which will create a new branch tagged with
your name):
```
mkvirtualenv -p $(which python3) clickchaim
git pull
git checkout -b ${USER}-cca-dev
git push -u origin ${USER}-cca-dev
make dev
```
If `make` exits with an error, you probably need to upgrade your pip version
```
pip3 install --upgrade pip --user
```
and try `make dev` again.

## Development Uninstall
To uninstall the dev version, delete the virtualenvironment, or
```
make uninstall
```
to keep the virtualenvironment intact, but uninstall this package.

## User Package Install
To install as a package to your python local libs
```
pip install chaim-cli --user
```

## Uninstall User Package
```
pip uninstall chaim-cli
```
