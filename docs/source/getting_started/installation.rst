.. _installation:

============
Installation
============

.. rst-class:: lead

   Install the **Hydrometeorology Calculation Library** as a Python package.

Requirements
============

- Python **3.12+**
- Recommended package manager: **pip** or `uv <https://docs.astral.sh/uv/getting-started/installation/>`_

``hydrometlib`` depends only on `Polars <https://docs.pola.rs/>`_, which is installed
automatically. pandas and NumPy are optional; install them only if you want to pass those types
in directly (see :ref:`flexible-inputs`).

Install options
===============

.. tab-set::
    :class: outline padded-tabs

    .. tab-item:: :iconify:`material-icon-theme:uv` uv

        Follow `uv installation instructions <https://docs.astral.sh/uv/getting-started/installation/>`_ if you
        haven't already.

        .. code-block:: bash

            uv add git+https://github.com/NERC-CEH/hydrometlib

    .. tab-item:: :iconify:`devicon:pypi` pip

        .. code-block:: bash

            pip install git+https://github.com/NERC-CEH/hydrometlib

Optional extras
===============

To pass pandas Series or NumPy arrays into the calculations, install the matching extra. The
``pandas`` extra also pulls in pyarrow.

.. tab-set::
    :class: outline padded-tabs

    .. tab-item:: :iconify:`material-icon-theme:uv` uv

        .. code-block:: bash

            # pandas Series support
            uv add "hydrometlib[pandas] @ git+https://github.com/NERC-CEH/hydrometlib"

            # NumPy array support
            uv add "hydrometlib[numpy] @ git+https://github.com/NERC-CEH/hydrometlib"

    .. tab-item:: :iconify:`devicon:pypi` pip

        .. code-block:: bash

            # pandas Series support
            pip install "hydrometlib[pandas] @ git+https://github.com/NERC-CEH/hydrometlib"

            # NumPy array support
            pip install "hydrometlib[numpy] @ git+https://github.com/NERC-CEH/hydrometlib"

Importing
=========

The calculations are grouped into four modules. Import the ones you need:

.. code-block:: python

   from hydrometlib import cosmos, evapotranspiration, flux, meteorology
