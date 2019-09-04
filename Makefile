SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq lambda/chaim-rotate-access-keys lambda/chaim-entry


.PHONY: $(SUBDIRS) tags clean build dev prod force depends


tags: $(SUBDIRS)
	ctags -R

depends: $(SUBDIRS)


clean: $(SUBDIRS)


build:
	./install_lambda.py -b dev


dev: build $(SUBDIRS)
	git add lambda/*/version && git commit -m "updating chaim version files" && git push


force: build $(SUBDIRS)
	git add lambda/*/version && git commit -m "updating chaim version files" && git push


prod: $(SUBDIRS)


$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
