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

Optional column arguments
=========================

A few functions have a column argument you can leave out. In the function reference these are typed
``pl.Expr | None`` and have a default of ``None``. When omitted, the calculation falls back to a
sensible default and the argument takes no part in the "same kind" or "same length" rules.

For example, :func:`~hydrometlib.evapotranspiration.potential_evapotranspiration_30min` takes an
optional ``wind_height`` column. Provide it (as a column, so it can vary over time) when the wind
sensor is not at 2 m; omit it when it is:

.. code-block:: python

    from hydrometlib import evapotranspiration as et

    # wind sensor at 2 m - no height correction
    et.potential_evapotranspiration_30min("rn", "g", "ta", "rh", "ws", "pa")

    # wind sensor height varies row by row
    et.potential_evapotranspiration_30min("rn", "g", "ta", "rh", "ws", "pa", "wind_height")

Rules
=====

**All column arguments in one call must be the same kind.** Pick one of ``pl.Expr``, column
name, ``pl.Series``, ``pd.Series`` or ``np.ndarray`` and use it for every column argument.
Mixing kinds gives a ``TypeError`` explaining which argument was which.

.. code-block:: python

    # fine - every column argument is a column name
    meteorology.net_radiation("swin", "swout", "lwin", "lwout")

    # TypeError - a column name mixed with an expression
    meteorology.net_radiation("swin", pl.col("swout") * 1.0, "lwin", "lwout")

    # TypeError - a pl.Series mixed with a pd.Series
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
