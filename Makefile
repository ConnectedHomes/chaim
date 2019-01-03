# SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq lambda/chaim-rotate-access-keys
SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq

.PHONY: $(SUBDIRS) tags clean build dev prod force

tags: $(SUBDIRS)
	ctags -R

clean: $(SUBDIRS)

build:
	./install_lambda.py -b dev

dev: build $(SUBDIRS)

force: build $(SUBDIRS)

prod: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
