.. _chaining:

=====================
Chaining calculations
=====================

.. rst-class:: lead

    A derived quantity is an input like any other.

Sometimes you'll have a pipeline that is two or three calculations deep. Because every calculation returns the same
form you passed in, the result of one is a valid argument to the next: in Polars you add it as a
column and refer to it by name, in Pandas you assign it and pass it straight back.

For example, estimate evapotranspiration from an eddy-covariance energy balance: first latent heat
flux from net radiation, soil heat flux and sensible heat flux, then evapotranspiration from that.

.. tab-set::

    .. tab-item:: :iconify:`simple-icons:polars` Polars
        :sync: polars

        .. literalinclude:: ../examples/chaining.py
           :language: python
           :start-after: [start:chaining_polars]
           :end-before: [end:chaining_polars]
           :dedent:

        .. jupyter-execute::
           :hide-code:

           from examples import chaining

           chaining.chaining_polars()

    .. tab-item:: :iconify:`devicon:pandas` Pandas
        :sync: pandas

        .. literalinclude:: ../examples/chaining.py
           :language: python
           :start-after: [start:chaining_pandas]
           :end-before: [end:chaining_pandas]
           :dedent:

        .. jupyter-execute::
           :hide-code:

           from examples import chaining

           chaining.chaining_pandas()

Some calculations exist mainly to feed others. The FAO-56 intermediates in
:mod:`~hydrometlib.evapotranspiration` - saturation vapour pressure, the psychrometric constant, the
slope of the vapour pressure curve - are available individually if you want to inspect them, but
:func:`~hydrometlib.evapotranspiration.potential_evapotranspiration_30min` computes them internally,
so you do not have to chain them by hand.
