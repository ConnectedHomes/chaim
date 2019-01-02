.PHONY: tags

tags:
	ctags -R

clean:
	../../install_lambda.py -c

dev:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py $(NOINC) dev
endif

prod:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	../../install_lambda.py prod
endif
