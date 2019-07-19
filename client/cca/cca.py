#!/usr/bin/env python3
#
# Copyright (c) 2018, Centrica Hive Ltd.
#
#     This file is part of chaim.
#
#     chaim is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     chaim is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with chaim.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Centrica Chaim cli using click module for command line parsing
"""

import os
import sys
import click
import threading
import cca.chaimcli as chaim
from cca.cliinifile import IniFile
from cca import __version__ as ccaversion


try:
    configfn = "~/.aws/credentials"
    config = IniFile(os.path.expanduser(configfn), takebackup=False)
    if "default" in config.titles():
        defsect = config.getSectionItems("default")
    else:
        config.add_section("default")
        defsect = config.getSectionItems("default")

    parkedfn = "~/.aws/chaim-parked"
    if not os.path.exists(parkedfn):
        # create an emppty file
        open(os.path.expanduser(parkedfn), "a").close()
    configparked = IniFile(os.path.expanduser(parkedfn), takebackup=False)
except FileExistsError:
    # create an empty config file
    open(os.path.expanduser(configfn), "a").close()
    config = IniFile(os.path.expanduser(configfn), takebackup=False)
    config.add_section("default")
    defsect = config.getSectionItems("default")


@click.group()
def cca():
    pass


@cca.command()
@click.option("-r", "--role", type=click.STRING, default="rro",
              help="Optional. The role to assume for this account, default rro")
@click.option("-d", "--duration", type=click.INT, default=1,
              help="Optional. Duration must be between 1-12 or 900-43,200, default 1")
@click.option("-a", "--alias", type=click.STRING, default="",
              help="Optional. Alias for the account name, to be used as the profile name")
@click.option("-D", "--default", is_flag=True, default=False,
              help="Optional. Set this account to be the default account profile to use")
@click.option("-R", "--region", help="Optional. Region, default eu-west-1")
@click.option("-T", "--terrible", is_flag=True, default=False,
              help="Add support for Terraform/Ansible to the credentials file")
@click.argument("account")
def account(account, role, duration, alias, default, region, terrible):
    """Configure credentials for AWS account ACCOUNT """
    setregion = False if region is None else region
    if not chaim.requestKeys(account, role, duration, alias, config, setregion, default, terrible):
        click.echo("Failed to obtain credentials for account " + account, err=True)


@cca.command()
def renew():
    """Renews all account credentials"""
    try:
        for section in config.titles():
            if section != "default":
                try:
                    threading.Thread(target=chaim.renewSection,args=(section,config)).start()
                    # if not chaim.renewSection(section, config):
                    #     click.echo("Failed to obtain credentials for account " + section, err=True)
                except chaim.UnmanagedAccount as e:
                    click.echo("{}".format(e))
                    pass
    except Exception as e:
        msg = "An error occurred: {}: {}".format(type(e).__name__, e)
        click.echo(msg, err=True)


@cca.command()
@click.argument("account", nargs=-1)
def gui(account):
    """Obtains a console session url and opens a browser window to it"""
    chaim.doUrl(account, config, browser=True)


@cca.command()
@click.argument("account", nargs=-1)
def url(account):
    """Obtains a console session url and copies it to the system clipboard"""
    chaim.doUrl(account, config)


@cca.command()
@click.argument("account", nargs=-1)
def gso(account):
    """Obtains a console session url, logs out of any other AWS session and opens a browser tab on the url"""
    chaim.doUrl(account, config, logout=True)


@cca.command()
@click.argument("initstring", nargs=-1)
def init(initstring):
    """Initialises the application for use with chaim"""
    chaim.doInit(initstring, config)


@cca.command()
def version():
    """Displays the version and exits."""
    click.echo(ccaversion)


@cca.command()
def list():
    """List all registered accounts and their expiry times"""
    chaim.displayMyList(config)


@cca.command()
def listall():
    """List all accounts available to chaim"""
    chaim.requestList(config)


@cca.command()
@click.argument("account", nargs=-1)
def delete(account):
    """Delete an accounts credentials"""
    if len(account) > 0:
        for acct in account:
            chaim.deleteAccount(acct, config)


@cca.command()
@click.argument("varpc")
def setautorenew(varpc):
    """Sets the percentage of time remaining before account is auto-renewed when requesting a url"""
    chaim.setVarPC(varpc, config)


@cca.command()
@click.argument("account")
def park(account):
    """Removes account from credentials and parks it for later use"""
    chaim.parkAccount(account, config, configparked)


@cca.command()
@click.argument("account")
def unpark(account):
    """Returns an account from parking to credentials and auto-renews it"""
    chaim.unparkAccount(account, config, configparked)


@cca.command()
def listpark():
    """List of parked accounts"""
    chaim.listParkAccounts(configparked)
