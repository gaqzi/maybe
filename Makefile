.PHONY: develop test

default: test

develop:
	pip install -r requirements.txt
	pip install -e .
	git submodule init && git submodule update

clean:
	find . -name '.cache' | xargs rm -rf
	find . -name '*.pyc' | xargs rm -rf
	rm -rf .tox

test:
	py.test
