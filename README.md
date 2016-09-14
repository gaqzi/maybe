radish
======

A task runner that understands version control.

# How to use

An example invocation of radish:

```
$ radish command tests --from 19abc023 --to 2514ecb1
Changed paths:
  - extensions/cool-extension/
  - frontend/js/

Running tests for extensions/cool-extension:
...........
OK

Running tests for .:
..........................
OK

All commands ended successfully and ran in 9.75s.
```

# Configuration

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

# Contributing

## Local development

To get started make with your current global version of Python do:

```shell
$ make develop 
$ make test
```

This will install all dependencies, check out the test repo, and then
run all the tests.

# License

Beerware License
