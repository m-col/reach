====================
Behavioural Training
====================

Usage
-----

:class:`Session` objects represent a single training session and are used to
operate the hardware during a session. After training, they are also used to
manipulate the collected behavioural data.

Training data is stored in a JSON file; each mouse has a single JSON file
containing all of its training data. At the top level, the JSON data is a
:class:`list` of :class:`dict`\s where each :class:`dict` contains data
collected during a single training session. This data can be manipulated at the
level of the :class:`Mouse`, which stores the data as a :class:`list` of
:class:`Session` objects.

We can add a new :class:`Session` to this list by running a training session.
Instantiate a :class:`Mouse` from the animal's training JSON by passing its ID
and the folder containing the data:

.. code-block:: python

    from reach import Mouse
    data_dir = '/path/to/data'
    mouse = Mouse.init_from_file(
        mouse_id='Mouse1',
        data_dir=data_dir,
    )

We need to create a backend for the new training session to control. We should
choose a backend base on the hardware setup that we want to use. For example,
if we are using Raspberry Pis then we can get that from :class:`reach` and
configure it how we like:

.. code-block:: python

    from reach.backends.RaspberryPi import RaspberryPi
    backend = RaspberryPi(
        reward_duration=60,
    )

See `Backends <backends.html>`_ to see how to create a new backend.

We can then begin the training session, providing some training settings and
any arbitrary metadata we'd like to save with the training data. When we are
done, we should save the data back to file:

.. code-block:: python

    mouse.train(
        backend,
        duration=1800,
        intertrial_interval=(4000, 6000),
        additional_data={'trainer': 'Matt', 'weight': 25.0},
    )
    mouse.save_data_to_file(data_dir)

An example script is found at :repo:`run_session.py
<blob/master/scripts/run_session.py>` to show how these steps can be extended.
