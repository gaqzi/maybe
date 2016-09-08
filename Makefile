.PHONY: develop test

default: test

develop:
	pip install -r requirements.txt
	pip install -e .
	git submodule init && git submodule update

test:
	py.test
