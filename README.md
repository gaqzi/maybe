maybe
=====

A tool to maybe run commands if something has changed

# How to use

An example invocation of maybe:

```
$ maybe run tests 19abc023 2514ecb1
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


You can see what files changed between two commits using `diff`:

```shell
$ maybe diff earlier-commit later-commit
extensions/cool-extension/somefile.py
frontend/js/package.json
```

# Configuration

maybe configuration is a yaml file named `Maybefile`, because I can.

```yaml
paths:
  - extensions/*/  # Mark each subdirectory in extensions as a path
  - frontend/js/
  
commands:  # Runs from the directory denoted by paths above
  tests:
    default: bin/rspec spec
    frontend/js/: npm test
```
