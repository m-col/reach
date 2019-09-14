==============
Data Structure
==============

Each :class:`Session` object contains an attribute named :class:`data`, which
unsurprisingly stores data for that training session. This includes behavioural
timepoints that record events during training, settings used for the session,
and any arbitrary metadata specified during training.

The behavioural timepoint data can then be used to analyse the mouse's
performance.

Data keys
---------

:class:`Session.data` is a :class:`dict`. Below lists the basic keys contained
within:


date : :class:`str`
    The date on which the training occurred in %Y-%m-%d format.

start_time and end_time : :class:`int`
    The start and end times of the session in Unix time.

duration : :class:`int`
    The duration of the session in seconds.

shaping : :class:`bool`
    Specifies if this session was a shaping session i.e. water is/was
    dispensed upon cue onset rather than successful grasp.

spout_count : :class:`int`
    The number of target spouts used in this session.

iti : :class:`tuple` of 2 :class:`int`\s
    The minimum and maximum inter-trial intervals.

cue_duration_ms : :class:`int`
    The duration in milliseconds for which the cue is illuminated in this
    session.

reward_duration_ms : :class:`int`
    The duration in milliseconds for which the solenoid is opened when is a
    reward is given.

spont_reach_spouts : :class:`list` of :class:`int`\s
    During training this stores pin numbers corresponding to spout touch
    sensors that detect spontaneous reaches during the inter-trial
    interval, then at the end of training this is converted to 0s and 1s to
    represent left or right spout.

spont_reach_timepoints : :class:`list` of :class:`int`\s
    This contains the timepoints (in Unix time) for all spontaneous
    reaches.

resets_timepoints : :class:`list` of 2 :class:`int`\s
    This list stores two lists, which each stores the timepoints (in Unix
    time) for all premature movements that reset the inter-trial interval
    for the left and right paws respectively.

cue_timepoints : :class:`list` of up to 2 :class:`list`\s of
:class:`int`\s
    The timepoints (in Unix time) at which the nth cue was illuminated
    at the start of a new trial.

touch_timepoints : :class:`list` of up to 2 :class:`list`\s of
:class:`int`\s
    The timepoints (in Unix time) at which the nth reach target was
    successfully grasped during a cued trial.

notes : :class:`str`
    Training notes made during the training session.

