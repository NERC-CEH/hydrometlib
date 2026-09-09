.. _quick-start:

===========
Quick start
===========

.. rst-class:: lead

    Turn measured columns into derived quantities, with Polars, Pandas or NumPy.

Every calculation in ``hydrometlib`` is a plain function: you give it the measured quantities it
needs, and it gives you the derived quantity back.

What you get back depends on what you put in:

- pass **Polars Series**, **Pandas Series** or **NumPy arrays** and the calculation runs
  immediately, returning the same type with the results;
- pass a **Polars expression** or a **column name** and you get a Polars *expression* back: a
  recipe you hand to ``select`` or ``with_columns`` for Polars to run.

Parameters that are single values rather than columns (a site altitude, a latitude, a calibration
coefficient) are passed as ordinary numbers.

Polars
======

Inside ``with_columns`` or ``select``, refer to columns by name (a plain string) or with
``pl.col``:

.. literalinclude:: ../examples/quick_start.py
   :language: python
   :start-after: [start:polars_expressions]
   :end-before: [end:polars_expressions]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import quick_start

   quick_start.polars_expressions()

You can also call a function with :class:`polars.Series` directly and get a Series straight back,
without a DataFrame:

.. literalinclude:: ../examples/quick_start.py
   :language: python
   :start-after: [start:polars_series]
   :end-before: [end:polars_series]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import quick_start

   quick_start.polars_series()

Pandas
======

Pass :class:`pandas.Series` (for example, columns of a DataFrame) and a Series comes back, ready
to assign as a new column:

.. literalinclude:: ../examples/quick_start.py
   :language: python
   :start-after: [start:pandas_series]
   :end-before: [end:pandas_series]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import quick_start

   quick_start.pandas_series()

Pandas support needs the ``pandas`` extra (see :ref:`installation`).

NumPy
=====

Pass :class:`numpy.ndarray` and an array comes back:

.. literalinclude:: ../examples/quick_start.py
   :language: python
   :start-after: [start:numpy_arrays]
   :end-before: [end:numpy_arrays]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import quick_start

   quick_start.numpy_arrays()

NumPy support needs the ``numpy`` extra (see :ref:`installation`).

Chaining calculations
=====================

A derived column can feed the next calculation. For example, estimate evapotranspiration from an
eddy-covariance energy balance: first latent heat flux from net radiation, soil heat flux and
sensible heat flux, then evapotranspiration from that.

.. tab-set::

    .. tab-item:: :iconify:`simple-icons:polars` Polars
        :sync: polars

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:chaining_polars]
           :end-before: [end:chaining_polars]
           :dedent:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.chaining_polars()

    .. tab-item:: :iconify:`devicon:pandas` Pandas
        :sync: pandas

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:chaining_pandas]
           :end-before: [end:chaining_pandas]
           :dedent:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.chaining_pandas()

Where to look next
==================

- :ref:`flexible-inputs`: the rules for what you can pass in and what comes back.
- :doc:`All calculations <../api/index>`: the full list of hydrometeorological calculations in the
  library, grouped by module, each with its inputs, units and source.
