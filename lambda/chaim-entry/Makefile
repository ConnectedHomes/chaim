LAMBDANAME = chaim-entry
SRC = app.py


.PHONY: tags clean prod force depends


tags:
	ctags -R


clean:


dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	mkdir -p vendor
	cp ../../version vendor/
	chalice deploy --stage=dev
	touch $@
endif


force:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	mkdir -p vendor
	cp ../../version vendor/
	chalice deploy --stage=dev
endif


prod:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	chalice deploy --stage=prod
endif
