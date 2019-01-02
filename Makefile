FIRSTSUB := lambda/chaim-cleanup
SUBDIRS := lambda/chaim-snsreq lambda/chaim-rotate-access-keys

.PHONY: $(SUBDIRS)

tags: $(SUBDIRS)
	ctags -R

clean: $(SUBDIRS)

dev: $(SUBDIRS)

prod: $(SUBDIRS)

$(FIRSTSUB):
	$(MAKE) -C $@ $(MAKECMDGOALS)

$(SUBDIRS): $(FIRSTSUB)
	export NOINC="-N"
	$(MAKE) -C $@ $(MAKECMDGOALS)
