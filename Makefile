SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq lambda/chaim-rotate-access-keys

.PHONY: $(SUBDIRS)

tags: $(SUBDIRS)
	ctags -R

clean: $(SUBDIRS)

dev: $(SUBDIRS)

prod: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
