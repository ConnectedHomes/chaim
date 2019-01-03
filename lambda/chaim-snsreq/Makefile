# chaim lambda in vpc makefile
SRC = chaim-cleanup.py chaimlib/botosession.py chaimlib/cognitoclient.py chaimlib/slackiamdb.py chaimlib/kmsclient.py chaimlib/glue.py chaimlib/envparams.py chaimlib/paramstore.py chaimlib/permissions.py chaimlib/wflambda.py chaimlib/utils.py

.PHONY: tags

tags: $(SRC)
	ctags -R

clean:
	../../install_lambda.py -c dev

dev: $(SRC)
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
