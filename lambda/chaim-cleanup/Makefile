# chaim-cleanup lambda
# the dev target creates an empty file called dev
# these are to ensure the dev lambda only get updated when 'something' has changed
# the prod lambda will always update when `make prod` is called

LAMBDANAME = chaim-cleanup
LARN = arn:aws:lambda:eu-west-1:627886280200:function:chaim-cleanup
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
	../../install_lambda.py -c dev


dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=sdev ../../install_lambda.py dev
	AWS_PROFILE=sdev aws events put-rule --name $(LAMBDANAME)-dev --schedule-expression "cron(13 3 ? * * *)" --state DISABLED
	AWS_PROFILE=sdev aws events put-targets --rule $(LAMBDANAME)-dev --targets "Id"=1,"Arn"="$(LARN)-dev"
	touch $@
endif


force:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=sdev ../../install_lambda.py dev
	AWS_PROFILE=sdev aws events put-rule --name $(LAMBDANAME)-dev --schedule-expression "cron(13 3 ? * * *)" --state DISABLED
	AWS_PROFILE=sdev aws events put-targets --rule $(LAMBDANAME)-dev --targets "Id"=1,"Arn"="$(LARN)-dev"
endif


prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	AWS_PROFILE=sadmin ../../install_lambda.py prod
	AWS_PROFILE=sadmin aws events put-rule --name $(LAMBDANAME)-prod --schedule-expression "cron(13 3 ? * * *)" --state DISABLED
	AWS_PROFILE=sadmin aws events put-targets --rule $(LAMBDANAME)-prod --targets "Id"=1,"Arn"="$(LARN)-prod"
endif


include $(SRC:.yaml=.d)
