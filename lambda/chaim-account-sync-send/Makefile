# chaim-account-sync-send lambda

LAMBDANAME = chaim-account-sync-send
SRC = $(LAMBDANAME).yaml

%.d: %.yaml
	../../depends.py

$(SRC):

depends:
	../../depends.py

tags: $(SRC)
	ctags -R

clean:
	../../install_lambda.py -c dev

prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=awsbilling ../../../install_lambda.py prod
endif
