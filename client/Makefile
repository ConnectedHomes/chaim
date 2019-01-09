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
majorv=$(shell grep 'majorv =' cca/__init__.py|cut -d" " -f3)
minorv=$(shell grep 'minorv =' cca/__init__.py|cut -d" " -f3)
buildv=$(shell grep 'buildv =' cca/__init__.py|cut -d" " -f3)
verstr=${majorv}.${minorv}.${buildv}

newbuildv=$(shell echo ${buildv}+1|bc)
newverstr=${majorv}.${minorv}.${newbuildv}

SRC = cca/cca.py cca/chaim.py cca/cliinifile.py cca/cliutils.py README.md setup.py

$(SRC):


tags:
	ctags -R


dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	pip uninstall -y chaim-cli
	sed -i "/^buildv =/s/.*$$/buildv = ${newbuildv}/" cca/__init__.py
	git add cca/__init__.py
	git commit -m "updating to ${newverstr}"
	git push
	pip install .
	touch $@
endif

uninstall:
	pip3 uninstall -y cca

install: dev
	# pip3 install -r requirements.txt --user
	pip3 install --user .

update:
	pip3 uninstall -y cca
	git pull
	pip3 install --user .
