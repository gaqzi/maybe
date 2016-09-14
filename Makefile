.PHONY: develop test

default: test

develop:
	pip install -r requirements.txt
	pip install -e .
	git submodule init && git submodule update
	echo -e "2.7.12\n3.4.5\n3.5.2" > .python-version
	@echo "#!/bin/sh\nmake pre-commit" > .git/hooks/pre-commit
	@echo "#!/bin/sh\nmake pre-push" > .git/hooks/pre-push
	@chmod a+x .git/hooks/pre-push .git/hooks/pre-push
	@echo
	@echo "Added pre-commit hook! To run manually: make pre-commit"
	@echo "Added pre-push hook! To run manually: make pre-push"

clean:
	find . -name '.cache' | xargs rm -rf
	find . -name '*.pyc' | xargs rm -rf
	rm -rf .tox

test:
	tox

coverage:
	py.test --cov=radish tests

lint:
	flake8 radish tests

pre-commit: coverage lint

pre-push: test
