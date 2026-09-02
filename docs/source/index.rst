.. _index:

:layout: landing

====================================
Hydrometeorology Calculation Library
====================================

.. rst-class:: lead

    A trusted library of verified and referenced hydrometeorological calculations and derivations.

Current version: |release|

.. container:: buttons

    `Getting started <getting_started/installation.html>`_
    `GitHub <https://github.com/NERC-CEH/hydrometlib>`_

``hydrometlib`` is a small, focused collection of the standard calculations used to turn raw hydrometeorological
measurements into derived quantities: net radiation, potential evapotranspiration, absolute humidity, soil moisture
from cosmic-ray neutron counts, and more. Each one is a single function you call with the data types you already have.

.. grid:: 1 1 3 3
    :gutter: 2
    :padding: 0
    :class-row: surface

    .. grid-item-card:: :octicon:`arrow-switch` Flexible inputs

        Call every function with a Polars expression, a column name, a Polars Series, a pandas
        Series, or a NumPy array. The result comes back in the same form you passed in.

    .. grid-item-card:: :octicon:`verified` Referenced and tested

        Every calculation cites the paper or standard it comes from, and is checked against
        known-good values in its unit tests, across all supported input types.

    .. grid-item-card:: :octicon:`shield-check` Trusted source

        Developed and maintained by `UKCEH <https://www.ceh.ac.uk/>`_ as part of the
        `Floods and Droughts Research Infrastructure (FDRI) <https://fdri.org.uk/>`_.

.. container:: image-row

   .. container:: image-item

      .. figure:: _static/UKCEH_Logo_Master_Black.png
         :alt: UKCEH
         :height: 100px
         :target: https://www.ceh.ac.uk

   .. container:: image-item

      .. figure:: _static/fdri_logo.png
         :alt: FDRI
         :height: 100px
         :target: https://fdri.org.uk

Community
=========

Developed at `UKCEH <https://www.ceh.ac.uk/>`_, welcoming community engagement and contributions.

License
=======

This project is licensed under the `MIT <https://github.com/NERC-CEH/hydrometlib/blob/main/LICENSE>`_.

.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Getting started

    getting_started/installation
    getting_started/quick_start

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: User guide

    user_guide/flexible_inputs

.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Function reference

    api/meteorology
    api/evapotranspiration
    api/flux
    api/cosmos

.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Developer guide

    developer/contributing
