SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq lambda/chaim-rotate-access-keys lambda/chaim-entry


.PHONY: $(SUBDIRS) tags clean build dev prod force depends


tags: $(SUBDIRS)
	ctags -R

depends: $(SUBDIRS)


clean: $(SUBDIRS)


build:
	./install_lambda.py -b dev


dev: build $(SUBDIRS)


force: build $(SUBDIRS)


prod: $(SUBDIRS)


$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
