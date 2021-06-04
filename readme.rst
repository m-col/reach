Reaching task for mice
======================

``reach`` is a small Python library for creating forelimb reaching tasks for
mice or other rodents used for neuroscientific research. It has been developed
for my own implementation of a Raspberry Pi-based visually-guided reaching task
using one or two reaching targets and visual stimuli -- both head-fixed and
freely-moving -- but has been designed to work with arbitrary 'backends' that
may implement other stimulus or reach target configurations. ``reach`` is
concerned with controlling hardware, responding to events during the task, and
organising the resulting data in a format that makes analysis easy.

The code and data representation follows a hierarchical object-oriented
structure:

+-------------+--------------------------------------------------------------------+
| Object      | Role                                                               |
+-------------+--------------------------------------------------------------------+
| ``Cohort``  | Manages one or more ``Mouse`` instances.                           |
|             | Useful for data handling and plotting.                             |
+-------------+--------------------------------------------------------------------+
| ``Mouse``   | Manages one or more ``Session`` instances.                         |
|             | Useful for analysing single animals and running training sessions. |
+-------------+--------------------------------------------------------------------+
| ``Session`` | Manages a training session's behavioural data and operates the     |
|             | training sessions.                                                 |
+-------------+--------------------------------------------------------------------+

Data is saved per animal in a JSON file. This data can be loaded as follows:

.. code-block:: python

    from reach import Mouse

    data_dir = '/path/to/your/data/'
    mouse = Mouse.init_from_file(
        mouse_id='Mouse1',
        data_dir=data_dir,
    )

A training session can be run, appending its results to the data stored in
``Mouse``. You would then want to save the data back to JSON to keep the new
data:

.. code-block:: python

    mouse.train(backend)
    mouse.save_data_to_file(data_dir)

``backend`` here is what interfaces with the hardware controlling the task.
Details on creating custom backends is `here
<https://m-col.github.io/reach/backends.html>`_.
