# chaim-cleanup lambda
# the dev target creates an empty file called dev
# these are to ensure the dev lambda only get updated when 'something' has changed
# the prod lambda will always update when `make prod` is called

LAMBDANAME = chaim-cleanup
SRC = $(LAMBDANAME).yaml

.PHONY: tags clean prod force

%.d: %.yaml
	../../depends.py

$(SRC):
	:


tags:
	ctags -R

clean:
	../../install_lambda.py -c dev

dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py dev
	touch $@
endif

force:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py dev
endif

prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py prod
endif

include $(SRC:.yaml=.d)
