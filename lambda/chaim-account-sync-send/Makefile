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

dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=awsbilling ../../install_lambda.py dev
	AWS_PROFILE=awsbilling aws events put-rule --name $(LAMBDANAME)-dev --schedule-expression "cron(13 3 ? * * *)" --state DISABLED
	AWS_PROFILE=awsbilling aws events put-targets --rule $(LAMBDANAME)-dev --targets "Id"=1,"Arn"="$(DEVLARN)-dev"
	touch $@
endif

prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=awsbilling ../../../install_lambda.py prod
endif
