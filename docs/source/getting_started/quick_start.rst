.. _quick-start:

===========
Quick start
===========

.. rst-class:: lead

    Turn measured columns into derived quantities, with Polars, Pandas or NumPy.

Every calculation in ``hydrometlib`` is a plain function: you give it the measured quantities it
needs, and it gives you the derived quantity back, in the same form you passed in.

Here is net radiation from its four measured components, in each of the three libraries:

.. tab-set::
    :class: outline padded-tabs

    .. tab-item:: :iconify:`simple-icons:polars` Polars
        :sync: polars

        Refer to columns by name (a plain string) or with ``pl.col``. You get a Polars *expression*
        back - which you can give to ``with_columns`` or ``select`` for Polars to run:

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:polars_expressions]
           :end-before: [end:polars_expressions]
           :dedent:

        Output:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.polars_expressions()

        You can also pass :class:`polars.Series` directly, and get a Series back, ready to assign:

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:polars_series]
           :end-before: [end:polars_series]
           :dedent:

        Output:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.polars_series()

    .. tab-item:: :iconify:`devicon:pandas` Pandas
        :sync: pandas

        Pass :class:`pandas.Series` - the columns of a DataFrame - and a Series comes back, ready to
        assign:

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:pandas_series]
           :end-before: [end:pandas_series]
           :dedent:

        Output:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.pandas_series()

        Pandas support needs the ``pandas`` extra (see :ref:`installation`).

    .. tab-item:: :iconify:`devicon:numpy` NumPy
        :sync: numpy

        Pass :class:`numpy.ndarray` and an array comes back:

        .. literalinclude:: ../examples/quick_start.py
           :language: python
           :start-after: [start:numpy_arrays]
           :end-before: [end:numpy_arrays]
           :dedent:

        Output:

        .. jupyter-execute::
           :hide-code:

           from examples import quick_start

           quick_start.numpy_arrays()

        NumPy support needs the ``numpy`` extra (see :ref:`installation`).

Every calculation in the library works this way. Which one to use, and what each argument means, is
in :doc:`All calculations <../api/index>`.

Where to look next
==================

- :ref:`flexible-inputs`: everything you can pass in and what comes back - including Polars Series,
  site attributes such as a sensor height or a wilting point, and evaluating a calculation for a
  single set of values.
- :ref:`chaining`: feeding one derived quantity into the next.
- :doc:`All calculations <../api/index>`: the full list of hydrometeorological calculations in the
  library, grouped by module, each with its inputs, units and source.
