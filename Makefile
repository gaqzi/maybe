.PHONY: develop test

default: test

develop:
	pip install -r requirements.txt
	pip install -e .
	git submodule init && git submodule update
	echo -e "2.7.12\n3.4.5\n3.5.2" > .python-version

clean:
	find . -name '.cache' | xargs rm -rf
	find . -name '*.pyc' | xargs rm -rf
	rm -rf .tox

test:
	py.test
