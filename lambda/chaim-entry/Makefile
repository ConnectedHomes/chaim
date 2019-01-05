LAMBDANAME = chaim-entry
SRC = $(LAMBDANAME).yaml


.PHONY: tags clean prod force depends


%.d: %.yaml
	../../depends.py


$(SRC):


depends:
	../../depends.py


tags:
	ctags -R


clean:


dev: $(SRC)
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


prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	chalice deploy --stage=prod
endif


include $(SRC:.yaml=.d)
