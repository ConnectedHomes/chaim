majorv=$(shell grep 'majorv =' ccu/__init__.py|cut -d" " -f3)
minorv=$(shell grep 'minorv =' ccu/__init__.py|cut -d" " -f3)
buildv=$(shell grep 'buildv =' ccu/__init__.py|cut -d" " -f3)
verstr=${majorv}.${minorv}.${buildv}

newbuildv=$(shell echo ${buildv}+1|bc)
newverstr=${majorv}.${minorv}.${newbuildv}


dev:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	pip uninstall -y cca
	sed -i "/^buildv =/s/.*$$/buildv = ${newbuildv}/" cca/__init__.py
	git add cca/__init__.py
	git commit -m "updating to ${newverstr}"
	git push
	pip install .
endif

uninstall:
	pip3 uninstall -y cca

install:
	# pip3 install -r requirements.txt --user
	pip3 install --user .
