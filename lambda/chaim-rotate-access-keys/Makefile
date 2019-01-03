SRC = chaim-rotate-access-keys.py chaimlib/botosession.py chaimlib/glue.py chaimlib/iamclient.py chaimlib/paramstore.py

.PHONY: tags

tags: $(SRC)
	ctags -R

clean:
	../../install_lambda.py -c dev

dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py -novpc dev
endif

prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py --novpc prod
endif
