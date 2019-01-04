
LAMBDANAME = chaim-cleanup
SRC = $(LAMBDANAME).yaml

.PHONY: tags clean prod force

%.d: %.yaml
	../../depends.py

$(SRC):


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
