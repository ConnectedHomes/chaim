# chaim-rotate-access-keys lambda
# the dev target creates an empty file called dev
# these are to ensure the dev lambda only get updated when 'something' has changed
# the prod lambda will always update when `make prod` is called

LAMBDANAME = chaim-rotate-access-keys
LARN = "arn:aws:lambda:eu-west-1:499223386158:function:chaim-rotate-access-keys"
SRC = $(LAMBDANAME).yaml

.PHONY: tags clean prod force

%.d: %.yaml
	../../depends.py

$(SRC):

requirements.txt:



tags: $(SRC)
	ctags -R

clean:
	../../install_lambda.py -c dev

dev: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py --novpc dev
	aws events put-rule --name $(LAMBDANAME)-dev --schedule-expression "rate(7 days)" --state DISABLED
	aws events put-targets --rule $(LAMBDANAME)-dev --targets "Id"=1,"Arn"="$(LARN)-dev"
	touch $@
endif

force:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py --novpc dev
	aws events put-rule --name $(LAMBDANAME)-dev --schedule-expression "rate(7 days)" --state DISABLED
	aws events put-targets --rule $(LAMBDANAME)-dev --targets "Id"=1,"Arn"="$(LARN)-dev"
endif


prod: $(SRC)
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py --novpc prod
	aws events put-rule --name $(LAMBDANAME)-prod --schedule-expression "rate(7 days)"
	aws events put-targets --rule $(LAMBDANAME)-prod --targets "Id"=1,"Arn"="$(LARN)-prod"
endif

include $(SRC:.yaml=.d)
