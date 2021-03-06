.PHONY: develop test

default: test

develop:
	pip install -r requirements.txt
	pip install -e .
	git submodule init && git submodule update
	echo "2.7.12\n3.4.5\n3.5.2" > .python-version
	@echo "#!/bin/sh\nmake pre-commit" > .git/hooks/pre-commit
	@echo "#!/bin/sh\nmake pre-push" > .git/hooks/pre-push
	@chmod a+x .git/hooks/pre-push .git/hooks/pre-push
	@echo
	@echo "Added pre-commit hook! To run manually: make pre-commit"
	@echo "Added pre-push hook! To run manually: make pre-push"

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean: clean-build
	find . -name '.cache' | xargs rm -rf
	find . -name '*.pyc' | xargs rm -rf
	rm -rf .tox .eggs

test:
	tox

coverage:
	py.test --cov=radish tests

lint:
	flake8 radish tests

pre-commit: coverage lint

pre-push: test

upload-package: test lint clean
	pip install twine wheel pypandoc
	python setup.py sdist bdist_wheel
	twine upload dist/*
