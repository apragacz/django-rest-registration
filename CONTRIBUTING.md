# Contributing to Django-REST-Registration


## Issues

Some tips on good issue reporting:

*   Choose the right template (Bug report, Feature request) when
    [creating an issue][project-new-issue].
    Try to preserve the proposed format of specific issue type,
    as it makes the maintainers work much easier to do.
*   When describing issues try to phrase your ticket in terms of
    the *behavior* you think needs changing rather than the *code*
    you think need changing.
*   Search the documentation and issue list first for related items,
    and make sure you're running the latest version of Django-REST-Registration
    before reporting an issue.
*   If reporting a bug, then try to include a pull request
    with a failing test case. This will help us quickly identify
    if there is a valid issue, and make sure that it gets fixed more quickly
    if there is one.
*   Closing an issue doesn't necessarily mean the end of a discussion.
    If you believe your issue has been closed incorrectly, explain why
    and we'll consider if it needs to be reopened.


### Security issues

If you think that you found a security issue (especially one with
high severity), please do not share it publicly;
instead, [write a direct e-mail](mailto:apragacz@o2.pl) to the author.


## Development

The easiest way to start developing Django-REST-Registration is cloning
the repository directly:

    git clone https://github.com/apragacz/django-rest-registration

But you should consider creating a fork and then cloning it:

    git clone git@github.com:yourusername/django-rest-registration.git

if you want to push your commited changes to GitHub and hopefully,
to contribute your changes back to upstream repository.


### Development setup

Django-REST-Registration uses [make][make] command to automate various tasks.
The `make` command has it's flaws but as
a [boring technology][boring-technology] is stable enough to serve its purpose.

You can list the available targets with the following command:

    make help

Assuming you are in the cloned repository and have Python 3.5+ installed:

    python3 -m venv .venv
    source .venv/bin/activate

Then, having your virtualenv set up, you can run:

    make install-dev


### Code checks

Code changes should follow the [PEP 8][pep-8] style conventions (with the
exception of limiting all lines to a maximum of 88 instead of 79 characters),
and we recommend you set up your editor to automatically indicate
non-conforming styles.

Ocassionaly, you may need to disable particular checks. For instance,
breaking a line to fit within 88 character limit is not possible;
in that case, disabling specific check (not the whole linter!) is allowed for
specific line (not the whole file!). Examples below:

```python
f(x)  # noqa: <errorcode>
f(x)  # pylint: disable=<errorcode>
```

There are several code check tools which Django-REST-Registration uses
to ensure code quality:

*   [flake8][flake8] (with additional plugins)
*   [isort][isort] (used as flake8 plugin)
*   [pylint][pylint]
*   [mypy][mypy]


With your repository set up, you can activate virtualenv:

    source .venv/bin/activate

And run the checks:

    make check

You can run linters separately:

    make flake8
    make mypy
    make pylint
    make check-docs

In addition there is package check as well, which builds the package
and performs checks on it:

    make check-package

### Testing

With your repository set up, and virtualenv activated, you can run the tests:

    make test

`make test` is just a wrapper around [py.test][pytest] so you can pass
any argument / option you would pass to the py.test executable with
the `ARGS` variable. For instance:

    make test ARGS="-v --cov --cov-report xml"

Or you call pytest directly:

    py.test -v --cov --cov-report xml


### Running against multiple environments

You can also use the excellent [tox][tox] testing tool to run the tests
against all supported versions of Python and Django.

Please note that tox is used when executing test by our CI setup
(currently we are using Circle CI).

Install `tox` globally, and then simply run:

    tox

If you don't want to install `tox` globally, you should be able
to run `tox` command within the virtualenv as well.

If you want to run all tox environments, you will need to have multiple versions
of Python installed (`3.6` - `3.11`). You will need to have GNU make installed
as well.

You can also run specific environment; for instance:

    tox -e py37-django30

You can list all available environments with:

    tox -l


## Pull requests

It's a good idea to make pull requests early on. A pull request represents
the start of a discussion, and doesn't necessarily need to be the final,
finished submission.

If the feature seems to be non-trivial, then even better, before starting
coding it makes sense to create a "Feature request" issue first and discuss
the potential solution.

It's also always best to make a new branch before starting work on
a pull request.  This means that you'll be able to later switch back
to working on another separate issue without interfering with
an ongoing pull requests.

It's also useful to remember that if you have an outstanding pull request then
pushing new commits to your GitHub repo will also automatically update
the pull requests.

GitHub's documentation for working on pull requests
is [available here][github-pull-requests].

Always run the tests before submitting pull requests:

    make check && make test

and ideally run `tox`
in order to check that your modifications are compatible on all
supported versions of Python and Django.

Once you've made a pull request take a look at the Circle CI build status in the
GitHub interface and make sure the tests are running as you'd expect.


# Documentation

The documentation for Django-REST-Registration is built by [Sphinx][sphinx]
from source files in [the docs directory][project-docs-src]
in [reStructuredText][rst] format.

Few single files like README and this Contributing Guildelines are written in
[Markdown][markdown].


## Building the documentation

With your repository set up, you can activate virtualenv:

    source .venv/bin/activate

And then run

    make build-docs

Then, the compiled documentation can be found
in your `docs/_build/html` subdirectory.

You can also edit the documentation iteratively; by running the script
in watch mode:

    make watch-docs

This will run a webserver
(by default on [127.0.0.1:8000](http://127.0.0.1:8000)) so you can watch
how the HTML documentation will change when you save your changes.

If you want to contribute your changes to the documentation as a PR,
please ensure that your changes don't generate any errors or warnings during
the building of the documentation (there is a check for that in our CI
just in case).


[project-new-issue]: https://github.com/apragacz/django-rest-registration/issues/new/choose
[project-issues]: https://github.com/apragacz/django-rest-registration/issues
[project-open-issues]: https://github.com/apragacz/django-rest-registration/issues?state=open
[project-docs-src]: https://github.com/apragacz/django-rest-registration/tree/master/docs

[github-pull-requests]: https://help.github.com/articles/using-pull-requests

[pep-8]: https://www.python.org/dev/peps/pep-0008/
[tox]: https://tox.readthedocs.io/
[flake8]: http://flake8.pycqa.org/
[isort]: https://github.com/timothycrosley/isort
[pylint]: https://www.pylint.org/
[mypy]: http://mypy-lang.org/
[pytest]: https://docs.pytest.org/
[markdown]: https://daringfireball.net/projects/markdown/basics
[rst]: http://docutils.sourceforge.net/docs/user/rst/quickref.html
[sphinx]: http://www.sphinx-doc.org/
[make]: https://www.gnu.org/software/make/manual/make.html
[boring-technology]: http://boringtechnology.club/
