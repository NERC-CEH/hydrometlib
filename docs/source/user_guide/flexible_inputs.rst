.. _flexible-inputs:

===============
Flexible inputs
===============

.. rst-class:: lead

    One function, whatever data you happen to have.

Every calculation takes your data in whichever of the common forms you already have it (a Polars
or Pandas column, a NumPy array) and hands the result back in the same form. You don't have to
convert your data first, and there aren't separate functions for different input types.

This page sets out exactly what each function accepts and returns.

Column arguments
================

The measured quantities a function takes (e.g. temperature, radiation, neutron counts... etc.) are
its **column arguments**. Each one accepts:

.. list-table::
    :header-rows: 1
    :widths: 20 20 60

    * - You pass
      - You get back
      - Notes
    * - ``pl.Expr``
      - ``pl.Expr``
      - Use the returned expression inside Polars Dataframe's methods such as ``select`` / ``with_columns``.
    * - ``str``
      - ``pl.Expr``
      - Shorthand for ``pl.col("name")``.
    * - ``pl.Series``
      - ``pl.Series``
      - Evaluated immediately.
    * - ``pd.Series``
      - ``pd.Series``
      - Evaluated immediately. Requires the ``pandas`` extra.
    * - ``np.ndarray``
      - ``np.ndarray``
      - Evaluated immediately. Requires the ``numpy`` extra.

The :ref:`quick-start` shows each of those forms side by side.

Attribute arguments
===================

Some parameters describe features of where the measurement was taken, for example: a sensor height, a latitude, a
wilting point, a calibration coefficient, etc. These are termed as *attributes*.

There are two ways that attributes can be provided:

1. When the attribute is static, simply pass in a number
2. When the attribute may vary across your data rows, pass a column-type (i.e. str, pl.Expr, pl.Series, pd.Series or
   np.ndarray)

.. literalinclude:: ../examples/flexible_inputs.py
   :language: python
   :start-after: [start:site_attributes]
   :end-before: [end:site_attributes]
   :dedent:

A number given for a site attribute takes no part in the "same kind" or "same length" rules below,
and it does not affect what you get back: the return type is still decided by the measured columns.

If a column-type is provided for an attribute, it must match the kind and length of all the other column inputs.

Rules
=====

**All column arguments in one call must be the same kind.**
Mixing kinds gives a ``TypeError`` explaining which argument was which. A site attribute given as a
*number* is exempt - it pairs with any kind - but given as a column it must match like any other.

.. literalinclude:: ../examples/flexible_inputs.py
   :language: python
   :start-after: [start:one_kind_per_call]
   :end-before: [end:one_kind_per_call]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import flexible_inputs

   flexible_inputs.one_kind_per_call()

**Series and array inputs must be the same length.** Passing Series or arrays of different
lengths raises a ``ValueError``:

.. literalinclude:: ../examples/flexible_inputs.py
   :language: python
   :start-after: [start:same_length]
   :end-before: [end:same_length]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import flexible_inputs

   flexible_inputs.same_length()

.. note::

   These checks are about the *kind* of thing you pass, not the data inside it. A Polars Series
   holding non-numeric values is an accepted container, so the error for it comes from Polars when
   the calculation runs, not from ``hydrometlib``.

Calling with only numbers
=========================

Give **every** argument as a number and there is no column to build against, so the calculation is
evaluated there and then and hands back a plain value instead:

.. literalinclude:: ../examples/flexible_inputs.py
   :language: python
   :start-after: [start:all_constant_call]
   :end-before: [end:all_constant_call]
   :dedent:

.. jupyter-execute::
   :hide-code:

   from examples import flexible_inputs

   flexible_inputs.all_constant_call()

This is handy for checking a value by hand.

Which form should I use?
========================

- Building up a table of derived columns in Polars: pass **column names**. It reads cleanly inside
  ``with_columns``.
- You already hold a **Series or array** and just want the numbers: pass it directly and use the
  result.
- Working with `time-stream <https://nerc-ceh.github.io/time-stream/>`_: pass column names or
  expressions and add the result with ``with_columns``.
- Checking a single set of values by hand: pass **numbers** for everything and read the result.
