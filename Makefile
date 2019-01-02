SUBDIRS := lambda/chaim-cleanup lambda/chaim-snsreq

.PHONY: $(SUBDIRS)

tags: $(SUBDIRS)

clean: $(SUBDIRS)

dev: $(SUBDIRS)

prod: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)
