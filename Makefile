SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq

.PHONY: $(SUBDIRS)

tags: $(SUBDIRS)
	ctags -R

clean: $(SUBDIRS)

dev: $(SUBDIRS)

prod: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
