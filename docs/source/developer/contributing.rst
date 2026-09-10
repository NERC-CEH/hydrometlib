.. _contributing:

=============
Contributing
=============

.. rst-class:: lead

    Help expand our Hydrometeorological calculation library.

Ways to contribute
==================

- Reporting bugs
- Suggesting new features and calculations
- Contributing to the codebase
  - Improving documentation
  - Adding unit tests
  - Fixing bugs or implementing new functionality

Reporting bugs
==============

We use GitHub issues to track any bugs you might find. Report a bug by opening a
`new issue <https://github.com/NERC-CEH/hydrometlib/issues>`_.

Before creating a bug report, please check that your bug has not already been reported.
If you find a closed issue that seems to report the same bug you're experiencing,
open a new issue and include a link to the original issue in your issue description.

Please include as many details as possible in your bug report. The information helps the maintainers
resolve the issue faster.

Suggesting new features
=======================

We use GitHub issues to track suggested enhancements to hydrometlib.
You can suggest an enhancement by opening a `new feature request <https://github.com/NERC-CEH/hydrometlib/issues>`_.
Before creating a new feature request, please check that a similar issue does not already exist.

Please describe the behavior you want and why, and provide examples of how hydrometlib would be used if your feature
were added.

Contributing to the codebase
============================

We welcome any contributions to the codebase of hydrometlib. That might be helping to improve documentation, adding
new unit tests to improve the robustness of the code, or going deeper to add new functionality.

**Contribution workflow**

1. Clone the repository
2. Create your feature branch (``git checkout -b feature/amazing-feature``)
3. Make your changes, with tests and documentation
4. Run the test suite and docs build (see `Testing`_ and :doc:`documentation`).
5. Commit your changes (``git commit -m 'Add some amazing feature'``)
6. Push to the branch (``git push origin feature/amazing-feature``)
7. Open a Pull Request

Adding a calculation
--------------------

Write the calculation as a pure Polars expression, annotate its column parameters ``pl.Expr``, and wrap it in
``@flexible``:

.. code-block:: python

    @flexible
    def net_radiation(swin: pl.Expr, swout: pl.Expr, lwin: pl.Expr, lwout: pl.Expr) -> pl.Expr:
        r"""Calculate net radiation (rn) [W m-2]
        ...
        """
        return swin - swout + lwin - lwout

``flexible`` lets callers pass a ``pl.Expr``, a column-name ``str``, a ``pl.Series``, a ``pd.Series`` or a
``np.ndarray`` and get the same kind back. No decorator can describe that transform to a type checker, so the
accepted types are declared as ``@overload``s in the module's ``.pyi`` stub. **You do not write those by hand** -
regenerate them from your signatures:

.. code-block:: bash

    make stubs

What the stub generator needs from you:

- Annotate a **data column** - a measured quantity, one value per row - ``pl.Expr``
- Annotate a **site attribute** ``Attribute``, imported from ``hydrometlib._dispatch``
- Reserve ``float`` for a quantity that can never be a column.

``flexible`` reads these annotations at runtime to work out how to carry out the calculation, so they have to be exact.

Your calculation also needs an entry in the function reference (see :doc:`documentation`) and tests covering each
input mode, ideally against a worked example from the paper or standard it cites.

Pull requests
-------------
Your pull request should follow these guidelines:

- **Title**: Add a broad title about what your changes are about
- **Description**:
    - Link to the issue you were working on.
    - Add any relevant information to the description that you think may help the maintainers review your code.
- Make sure your branch is **rebased** against the latest version of the main branch.
- Make sure all **GitHub Actions** checks pass.

After you have opened your pull request, a maintainer will review it and possibly leave some comments.
Once all comments are resolved, the maintainer will merge your pull request, and your work will be part of the next
hydrometlib release.

Code style and linting
======================

We enforce code style checks using ``ruff``, with configuration held in ``pyproject.toml``. You can run a check
to see if ruff finds any issues with the code style:

.. code-block:: bash

    ruff check

Ruff may be able to automatically fix issues:

.. code-block:: bash

    ruff check --fix

Ruff can also auto-format certain aspects of the code, using the config in ``pyproject.toml``
(which follows the default black settings):

.. code-block:: bash

    ruff format .

Pre commit hooks
----------------

Run below to setup the pre-commit hooks:

.. code-block:: bash

    git config --local core.hooksPath .githooks/

This will set this repo up to use the git hooks in the `.githooks/` directory.
The hook runs `ruff format --check` and `ruff check` to prevent commits that are not formatted correctly or have errors.
The hook intentionally does not alter the files, but informs the user which command to run before they can commit
successfully.

Testing
=======

We use `pytest` for running unit tests and coverage.

**Run all tests**

.. code-block:: bash

   pytest

**Check coverage**

.. code-block:: bash

   pytest --cov=hydrometlib --cov-report=term-missing

**Test only one file**

.. code-block:: bash

   pytest tests/hydrometlib/test_meteorology.py

**CI/CD**

GitHub Actions runs lint, type-check, tests, and docs build on every PR.
