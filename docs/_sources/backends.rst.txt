========
Backends
========

Throughout training, the :class:`Session` that we are using controls the
sequence of events, but does not directly control any hardware. Instead, a
backend is specified, allowing for different backends to be used. Backends
directly control any hardware (or software), having their methods called by the
running :class:`Session`. New backends can be created for use during training
by creating a subclass of :class:`reach.backends.Backend` and overriding its
methods.

Backends are passed to :class:`Session` either indirectly via
:class:`Mouse.train`, or directly to :class:`Session.run`. The backend should
be instantiated before passing it; this allows for configuration of the backend
in a manner that is specific to the type of backend being used.

The running :class:`Session`, before training begins, passes itself to the
backend's :class:`configure_callbacks` method so that the backend can access a
number of functions that should be assigned to specific behavioural events as
callbacks. The backend can wrap or modify these functions if it requires.
During training, the :class:`Session` will call :class:`backend.start_iti` and
:class:`backend.start_trial` at the appropriate time, in which the backend
should assign the callback functions to their corresponding events.

See :repo:`mock.py <blob/master/reach/backends/mock/mock.py>` for a minimal
example, or :repo:`raspberry.py
<blob/master/reach/backends/raspberrypi/raspberry.py>` for a full example that
controls the GPIO pins on a Raspberry Pi.
