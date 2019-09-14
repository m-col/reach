============
Introduction
============

Overview
--------

This project contains directions on how to contruct, operate and analyse a
head-fixed forelimb reaching task for mice. This design uses visual cues as
reach targets, though the design could easily be adapted to be cued via other
sensory modalities.

This Python library is used by a Raspberry Pi to control the hardware of the
behavioural task, and is then used to manipulate the data collected during
training.

Installation
------------

Simply clone :class:`reach`:

.. code-block:: bash

    git clone https://github.com/m-col/reach

Then either add the folder to :class:`PYTHONPATH` or install using setup.py:

.. code-block:: bash

    python setup.py build
    python setup.py install --user
