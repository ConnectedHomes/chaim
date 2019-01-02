SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq lambda/chaim-rotate-access-keys

.PHONY: $(SUBDIRS)

tags: $(SUBDIRS)
	ctags -R

clean: $(SUBDIRS)

build:
	./install_lambda.py -b dev

dev: build $(SUBDIRS)

prod: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
