==============
Data Structure
==============

:class:`Session`\s have a :class:`data` attribute which stores data for that
training session. This includes behavioural timepoints that record events
during training, settings used for the session, and any arbitrary metadata
specified by the user.

Keys
----

:class:`Session.data` is a :class:`dict`. Below lists the default keys
contained within that are created during a training session:

.. list-table::
   :widths: 25 75

   * - duration (:class:`int`)
     - The duration of the session in seconds.

   * - date (:class:`str`)
     - The date of training in %Y-%m-%d format.

   * - start_time (:class:`float`)
     - The start time of the session in Unix time.

   * - end_time (:class:`float`)
     - The end time of the session in Unix time.

   * - trials (:class:`list` of :class:`dict`\s)
     - This list stores the main behavioural data. Each element is a dictionary
       containing, for every trial, the start time, lift time, lift paw, target
       spout, spout position, cue duration, outcome, and whether or not the
       trial is a shaping trial.

   * - intertrial_interval (:class:`tuple` of 2 :class:`int`\s)
     - The minimum and maximum inter-trial intervals. The inter-trial interval
       for a given trial is randomly determined between these two values.

   * - spontaneous_reaches (:class:`list` of :class:`tuple`\s)
     - This list contains, for every spontaneous reach, a tuple indicating the
       timepoint (in Unix time) and which spout was grasped.

   * - resets (:class:`list` of :class:`tuple`\s)
     - Like spontaneous_reaches above, this list stores, for every premature
       movement that reset the intertrial interval, the timepoint (in Unix
       time) and which paw was lifted to cause the reset.
