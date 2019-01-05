LAMBDANAME = chaim-entry


.PHONY: tags clean prod force depends


tags:
	ctags -R


clean:


dev:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	chalice deploy --stage=dev
	touch $@
endif


force:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	chalice deploy --stage=dev
endif


prod:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	chalice deploy --stage=prod
endif
