.. _flexible-inputs:

===============
Flexible inputs
===============

.. rst-class:: lead

    One function, whatever data you happen to have.

Every calculation takes your data in whichever of the common forms you already have it (a Polars
or Pandas column, a NumPy array) and hands the result back in the same form. You don't have to
convert your data first, and there isn't a separate function for Pandas and for Polars.

This page sets out exactly what each function accepts and returns.

Column arguments
================

The measured quantities a function takes (temperature, radiation, neutron counts, and so on) are
its *column arguments*. Each one accepts:

.. list-table::
    :header-rows: 1
    :widths: 30 30 40

    * - You pass
      - You get back
      - Notes
    * - ``pl.Expr``
      - ``pl.Expr``
      - Use inside ``select`` / ``with_columns``.
    * - column-name ``str``
      - ``pl.Expr``
      - Shorthand for ``pl.col("name")``.
    * - ``pl.Series``
      - ``pl.Series``
      - Evaluated immediately.
    * - ``pd.Series``
      - ``pd.Series``
      - Requires the ``pandas`` extra.
    * - ``np.ndarray``
      - ``np.ndarray``
      - Requires the ``numpy`` extra.

The return type always matches what you put in. Passing expressions or column names builds a new
expression for Polars to evaluate later; passing a Series or array runs the calculation there and
then and gives you a Series or array back.

Constant arguments
==================

Some parameters are not columns: a site altitude, a latitude, a calibration coefficient, a
threshold. These are *constant arguments* and take a single number (``int`` or ``float``). They
are the same for every row.

.. code-block:: python

    from hydrometlib import cosmos

    cosmos.volumetric_water_content(
        "cts_mod_corr",       # column argument
        ref_soc=0.01,         # constant arguments from here on
        ref_bulkdensity=1.35,
        ref_latticewater=0.02,
        n0_mod=2000,
        n_min=400,
        n_max=4000,
    )

In the function reference, constant arguments are the ones typed ``float`` rather than ``pl.Expr``.

Rules
=====

**All column arguments in one call must be the same kind.** Mix a ``pl.Series`` with a
``pd.Series`` in the same call and you get a ``TypeError`` explaining which argument was which.
Column names and expressions count as the same kind and can be combined.

.. code-block:: python

    # fine - str and pl.Expr together
    meteorology.net_radiation("swin", pl.col("swout") * 1.0, "lwin", "lwout")

    # TypeError - pl.Series and pd.Series in one call
    meteorology.net_radiation(pl.Series(...), pd.Series(...), pl.Series(...), pl.Series(...))

**Series and array inputs must be the same length.** Passing Series or arrays of different
lengths raises a ``ValueError``.

**Column arguments only take numeric data.** Passing something that is not a number (or, for a
column argument, not one of the accepted container types) raises a ``TypeError`` naming the
argument.

Which form should I use?
========================

- Building up a table of derived columns in Polars: pass **column names**. It reads cleanly inside
  ``with_columns``.
- You already hold a **Series or array** and just want the numbers: pass it directly and use the
  result.
- Working with `time-stream <https://nerc-ceh.github.io/time-stream/>`_: pass column names or
  expressions and add the result with ``with_columns``.
