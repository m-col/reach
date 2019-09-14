====================
Behavioural Training
====================

Usage
-----

:class:`Session` objects represent a single training session and are first used
to operate the hardware during a session. They are subsequently used to
manipulate the data collected during that session for analysis.

Training data is stored in a JSON file; each mouse has a single JSON file
containing all of its training data. At the top level, the JSON data is a
:class:`list` of :class:`dict`\s where each :class:`dict` corresponds to the nth
training day. This data is collated and manipulated together at the level of
the :class:`Mouse`, in the form of a :class:`list` of :class:`Session`
objects.

A :class:`Mouse` is instantiated from its corresponding training JSON by
passing the mouse's ID and the path to the folder containing the training
JSONs:

.. code-block:: python

    mouse = Mouse.init_from_file(
        mouse_id='ExampleMouse1',
        json_path='~/training_data',
    )

The :class:`Mouse.train` method creates a new :class:`Session` object and
begins the training session:

.. code-block:: python

    mouse.train(
        config_file='~/reach_config.ini',
        data={'trainer': 'Matt', 'training_box': 1},
    )

Here, we are passing the path to a config file which contains the training
settings (`more info below <#training_settings>`_), and a :class:`dict`
containing any arbitrary data that we'd like to save alongside this session's
data.

Finally we save the training data back into the JSON file:

.. code-block:: python

    mouse.save_data_to_file('~/training_data')

There is an example script at :repo:`scripts/run_session/py
<blob/master/scripts/run_session.py>` which uses argparse to take input from
the user and run a training session.


Training settings
-----------------

Configuration settings of a training session can be passed to
:class:`Session.run(config)` to change some of the task parameters. The
:class:`Mouse.train()` method can accept a :class:`str` providing a path to a
config file, which it will read settings from and use these to run a session:

.. code-block:: python

    mouse.train(
        config_file='~/reach_config.ini',
    )

Default values will be used if it is not passed, or the file does not exist.

A config file with default values can be generated on demand:

.. code-block:: python

    reach.generate_config('~/reach_config.ini')
