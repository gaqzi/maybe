radish
======

[![CircleCI](https://circleci.com/gh/gaqzi/radish.svg?style=shield)](https://circleci.com/gh/gaqzi/radish)
[![Latest Version](https://img.shields.io/pypi/v/gocd-cli.svg)](https://pypi.python.org/pypi/radish-run/)
[![Python versions](https://img.shields.io/pypi/pyversions/gocd-cli.svg)](https://pypi.python.org/pypi/radish-run/)

Radish is a task runner that understands version control. 

You define a command that applies to multiple subprojects in your repository
and thenradish will figure out which projects have changed and run the
command for just those projects. Radish isn't a replacement for make, gulp,
gradle, rake, or any other task runner. It's a supplement for
orchestrating other runners and scripts with some smarts from your
version control repository.

If you're using a [CI]/[CD] server like [Concourse] or [GoCD] which
supports pipelines as first-class citizens you probably have no need for
radish on your CI/CD server. It might still be useful on your dev
machine, though.

[CI]: https://en.wikipedia.org/wiki/Continuous_integration
[CD]: https://en.wikipedia.org/wiki/Continuous_delivery
[Concourse]: https://concourse.ci/
[GoCD]: https://www.go.cd/

## Installation

Radish is available on PyPi as [radish-run] and can be installed on most
systems with pip:

```shell
$ pip install radish-run
```

[radish-run]: https://pypi.python.org/pypi/radish-run/

## How to use

An example invocation of radish:

```shell
$ radish command tests --from 19abc023 --to 2514ecb1
Changed paths:
  - extensions/cool-extension/
  - frontend/js/

Running tests for extensions/cool-extension/:
...........
OK

Running tests for frontend/js/:
..........................
OK

All commands ended successfully and ran in 9.75s.
```

## Configuration

radish configuration is a yaml file named `Radishfile`, because I can.

```yaml
paths:
  - extensions/*/  # Mark each subdirectory in extensions as a path
  - frontend/js/
  
commands:  # Runs from the directory denoted by paths above
  tests:
    default: bin/rspec spec
    frontend/js/: npm test
```

## An example use case

Take that you're building a single page web app, it consists of two parts: 
- The backend that delivers JSON
- The frontend that holds all the clicky bits that end-users see

Because cross-functional teams this project is in one repository, which
is a great win for productivity. But it has a downside: when there are
only changes to the backend, then all the tests for the frontend is
still run. Finally, after running all tests it can get deployed, but
then both sites get deployed despite nothing changing on the frontend.

So this is a crazy situation. It shouldn't be. So this is where radish
comes in. You tell radish about `test` and `deploy`, and what that means
for both the backend and the frontend, then on your CI server you run
the commands with the last green commit. Radish then figures out what
has changed from the current commit and the last one, and only runs the
command for those projects.

## Contributing

### Roadmap

- Define a path/project to always run, no matter whether there are
  changes or not
  - Run a different command if there are changes to the project
- Allow for changed files to be passed in to commands. Primarily a
  feature for local dev boxes, so you only run the command against
  changed files.
- Dependencies between projects. If the `frontend-payment` project
  changes then run the command in the `frontend` project as well.
- Custom differs for Ci systems so they can smartly figure out what
  the last green commit was, instead of relying on `HEAD~1` as the
  poor mans "what was the last change?"

### Local development

To get started make with your current global version of Python do:

```shell
$ git clone https://github.com/gaqzi/radish.git
$ cd radish/
$ make develop
$ make test
```

This will install all dependencies, check out the test repo, and then
run all the tests.

## License

Beerware License
