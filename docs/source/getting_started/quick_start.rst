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

.. code-block:: python

    import polars as pl
    from hydrometlib import meteorology

    df = pl.DataFrame(
        {
            "swin": [22.9, 19.3, 14.0, 25.1],
            "swout": [4.9, 4.2, 3.0, 5.5],
            "lwin": [24.1, 26.0, 26.2, 23.1],
            "lwout": [31.2, 31.9, 30.9, 30.8],
        }
    )

    df = df.with_columns(
        rn=meteorology.net_radiation("swin", "swout", "lwin", "lwout")
    )

.. code-block:: text

    shape: (4, 5)
    ┌──────┬───────┬──────┬───────┬──────┐
    │ swin ┆ swout ┆ lwin ┆ lwout ┆ rn   │
    │ ---  ┆ ---   ┆ ---  ┆ ---   ┆ ---  │
    │ f64  ┆ f64   ┆ f64  ┆ f64   ┆ f64  │
    ╞══════╪═══════╪══════╪═══════╪══════╡
    │ 22.9 ┆ 4.9   ┆ 24.1 ┆ 31.2  ┆ 10.9 │
    │ 19.3 ┆ 4.2   ┆ 26.0 ┆ 31.9  ┆ 9.2  │
    │ 14.0 ┆ 3.0   ┆ 26.2 ┆ 30.9  ┆ 6.3  │
    │ 25.1 ┆ 5.5   ┆ 23.1 ┆ 30.8  ┆ 11.9 │
    └──────┴───────┴──────┴───────┴──────┘

You can also call a function with :class:`polars.Series` directly and get a Series straight back,
without a DataFrame:

.. code-block:: python

    swin = pl.Series("swin", [22.9, 19.3])
    swout = pl.Series("swout", [4.9, 4.2])
    lwin = pl.Series("lwin", [24.1, 26.0])
    lwout = pl.Series("lwout", [31.2, 31.9])

    meteorology.net_radiation(swin, swout, lwin, lwout)
    # shape: (2,)
    # Series: 'net_radiation' [f64]
    # [
    #     10.9
    #     9.2
    # ]

Pandas
======

Pass :class:`pandas.Series` (for example, columns of a DataFrame) and a Series comes back, ready
to assign as a new column:

.. code-block:: python

    import pandas as pd
    from hydrometlib import meteorology

    df = pd.DataFrame(
        {
            "swin": [22.9, 19.3, 14.0, 25.1],
            "swout": [4.9, 4.2, 3.0, 5.5],
            "lwin": [24.1, 26.0, 26.2, 23.1],
            "lwout": [31.2, 31.9, 30.9, 30.8],
        }
    )

    df["rn"] = meteorology.net_radiation(df["swin"], df["swout"], df["lwin"], df["lwout"])

.. code-block:: text

       swin  swout  lwin  lwout    rn
    0  22.9    4.9  24.1   31.2  10.9
    1  19.3    4.2  26.0   31.9   9.2
    2  14.0    3.0  26.2   30.9   6.3
    3  25.1    5.5  23.1   30.8  11.9

Pandas support needs the ``pandas`` extra (see :ref:`installation`).

NumPy
=====

Pass :class:`numpy.ndarray` and an array comes back:

.. code-block:: python

    import numpy as np
    from hydrometlib import meteorology

    swin = np.array([22.9, 19.3])
    swout = np.array([4.9, 4.2])
    lwin = np.array([24.1, 26.0])
    lwout = np.array([31.2, 31.9])

    meteorology.net_radiation(swin, swout, lwin, lwout)
    # array([10.9,  9.2])

NumPy support needs the ``numpy`` extra (see :ref:`installation`).

Chaining calculations
=====================

A derived column can feed the next calculation. For example, estimate evapotranspiration from an
eddy-covariance energy balance: first latent heat flux from net radiation, soil heat flux and
sensible heat flux, then evapotranspiration from that.

.. tab-set::

    .. tab-item:: :iconify:`simple-icons:polars` Polars
        :sync: polars

        .. code-block:: python

            import polars as pl
            from hydrometlib import flux

            df = pl.DataFrame(
                {
                    "rn": [80.0, 120.0],
                    "shf": [5.0, 8.0],
                    "h": [30.0, 40.0],
                    "ta": [15.0, 18.0],
                }
            )

            df = df.with_columns(
                le=flux.latent_heat_flux("rn", "shf", "h"),
            ).with_columns(
                et=flux.evapotranspiration_from_latent_heat_flux("le", "ta"),
            )

    .. tab-item:: :iconify:`devicon:pandas` Pandas
        :sync: pandas

        .. code-block:: python

            import pandas as pd
            from hydrometlib import flux

            df = pd.DataFrame(
                {
                    "rn": [80.0, 120.0],
                    "shf": [5.0, 8.0],
                    "h": [30.0, 40.0],
                    "ta": [15.0, 18.0],
                }
            )

            df["le"] = flux.latent_heat_flux(df["rn"], df["shf"], df["h"])
            df["et"] = flux.evapotranspiration_from_latent_heat_flux(df["le"], df["ta"])

Where to look next
==================

- :ref:`flexible-inputs`: the rules for what you can pass in and what comes back.
- **Function reference** (in the sidebar): every function, grouped by module, with its inputs,
  units and source.
