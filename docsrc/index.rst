=====
reach
=====

:class:`reach` is a Python library that operates a forelimb reaching task for
mice. It also aims to make handling and analysis of behavioural data collected
during the task easy and straightforward.

This documentation contains directions on how to contruct, operate and analyse
a head-fixed forelimb reaching task for mice. Different backends can be used
during the task to interface with the hardware, allowing for customisation of
the training paradigm. This facilitates modification of the task to, for
example, use different types of cues. The original backend controls a Raspberry
Pi and its inputs and outputs.

GitHub: |repo|


Installation
------------

Simply clone with git:

.. code-block:: bash

    git clone https://github.com/m-col/reach

Then either add the folder to :class:`PYTHONPATH` or install using setuptools:

.. code-block:: bash

    python setup.py build
    python setup.py install --user


.. toctree::
   :hidden:
   :maxdepth: 2

   training
   backends
   API
   data
