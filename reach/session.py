"""
Sessions
========

:class:`Session` objects interface with a backend such as a raspberry pi to operate
training sessions and record data.
"""


import json
import random
import signal
import sys
import textwrap
import time
from collections import deque

import reach.backends
from reach.utilities import cache


# Number of recent trials used to calculate adaptive task settings
_SLIDING_WINDOW = 10


class TrialDeque(deque):
    """
    This lets the Session do e.g. recent_trials.shaping to return a list containing the
    values stored in all trials in the deque (which are themselves dicts).
    """
    def __getattr__(self, name):
        if len(self) == 0:
            return []
        return [x[name] for x in self]


class Session:
    """
    Controls a single training session and its behavioural data.

    Parameters
    ----------
    data : :class:`dict`, optional
        A dictionary of additional or pre-filled data to be added to the session's
        training data.

    """
    def __init__(self, data=None):
        self.data = data or {}

        # These attributes track state during training
        self._reward_count = 0
        self._outcome = 0
        self._iti_broken = False
        self._current_spout = 0
        self._water_at_cue_onset = None
        self._backend = None
        self._message = print
        self._extended_trial = False
        self._cue_duration = 10000
        self._recent_trials = TrialDeque([], _SLIDING_WINDOW)
        self._spout_position = 1

    @classmethod
    def init_all_from_file(cls, full_path):
        """
        Generate a :class:`list` of :class:`Session` objects from data stored in a
        Training JSON.

        Parameters
        ----------
        full_path : :class:`str`
            Full path to file containing existing training data.

        """
        with open(full_path, 'r') as fd:
            previous_data = json.load(fd)

        training_data = [
            cls(data=data) for data in previous_data
        ]

        return training_data

    def add_data(self, data):
        """
        Manually add data to the Session's data.

        Parameters
        ----------
        data : :class:`dict`
            Dictionary of values to add into the session's data.

        """
        self.data.update(data)

    def run(
        self,
        backend,
        duration=None,
        intertrial_interval=None,
        previous_data=None,
    ):
        """
        Begin a training session.

        Parameters
        ----------
        backend : :class:`class`
            An instance of a :class:`Backend` subclass.

        duration : :class:`int`, optional
            Duration of the training session in seconds. Default: 1800 seconds.

        intertrial_interval : :class:`tuple` of 2 :class:`int`\s, optional
            Minimum and maximum duration in milliseconds for use for the inter-trial
            interval. Default: (4000, 6000).

        previous_data : :class:`dict` of training data, optional
            Training data from the previous session, which if provided will be used when
            calculating initial cue duration, spout position and shaping status.

        """
        if not isinstance(backend, reach.backends.Backend):
            raise SystemError(
                'Provided backend is not an instance of reach.backend.Backend'
            )
        self._backend = backend

        if hasattr(self._backend, 'message'):
            self._message = self._backend.message

        self.data['duration'] = duration or 1800
        self.data['intertrial_interval'] = intertrial_interval or (4000, 6000)
        self.data['trials'] = []
        self.data['resets'] = []
        self.data['spontaneous_reaches'] = []

        if previous_data and previous_data['trials']:
            self._recent_trials.extend(previous_data['trials'])
            self._spout_position = self._recent_trials[-1]['spout_position']
            self._cue_duration = self._recent_trials[-1]['cue_duration']

        self._backend.position_spouts(self._spout_position)
        self._display_training_settings()
        self._backend.configure_callbacks(self)

        try:
            self._backend.wait_to_start()
        except KeyboardInterrupt:
            self._backend.cleanup()
            self._message('Cancelled..')
            sys.exit(1)

        signal.signal(signal.SIGINT, self._end_session)
        self._backend.disable_spouts()
        self._trial_loop()
        self._end_session()

    def _display_training_settings(self):
        """
        Display the training settings that will be used for the upcoming training
        session.
        """
        iti_min, iti_max = self.data['intertrial_interval']

        self._message(textwrap.dedent(f"""
            _________________________________

            Duration:               {self.data['duration']} s
            Inter-trial interval:   {iti_min} - {iti_max} ms
            Initial cue duration:   {self._cue_duration} ms
            Initial spout position: {self._spout_position}
            _________________________________
        """))

    def _trial_loop(self):
        """
        Loop over the main event sequence forming the behavioural task.
        """
        data = self.data
        now = time.time()
        data['start_time'] = now
        data['end_time'] = now + data['duration']

        trial_count = 0

        while now < data['end_time']:
            trial_count += 1
            self._outcome = 0
            self._message("_____________________________________")
            self._message("# -- Starting trial #%i -- %4.0f s -- #"
                          % (trial_count, now - data['start_time']))
            self._adapt_settings()
            if self._inter_trial_interval():
                self._trial()
                self._message(f"Total rewards: {self._reward_count}")
                now = time.time()

            if self._outcome == 3:
                break

    def _adapt_settings(self):
        """
        Adapt live training settings based on recent behavioural performance.
        """
        if self._recent_trials and self._recent_trials[-1]['outcome'] == 1:
            self._current_spout = random.randint(0, 1)

        num_hits = self._recent_trials.outcome.count(1)

        if num_hits >= _SLIDING_WINDOW * 0.90:
            self._water_at_cue_onset = False
            if self._recent_trials.shaping.count(False) < 3:
                return

            if self._spout_position < 7:
                if len(set(self._recent_trials.spout_position[-3:])) == 1:
                    self._spout_position += 1
                    self._backend.position_spouts(self._spout_position)
                    self._message(
                        f'Spouts progressed to position {self._spout_position}'
                    )
                    time.sleep(1)
                    self._backend.disable_spouts()

            elif len(set(self._recent_trials.spout_position[-3:])) == 1:
                if self._cue_duration > 2000:
                    self._cue_duration = max(int(self._cue_duration * 0.9), 2000)
                    self._message(f'Cue duration decreased to {self._cue_duration} ms')

        elif num_hits == 0:
            self._water_at_cue_onset = True
            self._message('Shaping.')

    def _inter_trial_interval(self):
        """
        Run inter-trial interval during training session.

        During the inter-trial interval we start listening for mouse movements using the
        touch sensors. Shaping can be toggled by pressing the start button.
        """
        self._backend.start_iti()
        self._extended_trial = False
        self._iti_broken = True

        while self._iti_broken:
            self._backend.wait_for_rest()
            self._iti_broken = False

            now = time.time()
            iti_duration = random.uniform(*self.data['intertrial_interval']) / 1000
            trial_end = now + iti_duration
            self._message(f"Counting down {iti_duration:.2f}s")

            while now < trial_end and not self._iti_broken:
                if self._outcome == 3:
                    return False
                time.sleep(0.020)
                now = time.time()

        return True

    def _trial(self):
        """
        Run trial during training session.
        """
        now = time.time()
        self.data['trials'].append({'start': now})

        self._backend.start_trial(self._current_spout)
        if self._water_at_cue_onset:
            self._backend.dispense_water(self._current_spout)

        if self._extended_trial:
            cue_duration = self.data['end_time'] - now
        else:
            cue_duration = self._cue_duration / 1000
        cue_end = now + cue_duration

        while not self._outcome and now < cue_end:
            time.sleep(0.008)
            now = time.time()

        if self._outcome == 0:
            self._backend.end_trial()
            self._backend.miss_trial()
            self._message("Missed reach")
            self.data['trials'][-1]['end'] = cue_end

        elif self._outcome == 1:
            self._message("Successful reach!")
            self._reward_count += 1

        elif self._outcome == 2:
            self._message("Incorrect reach!")

        elif self._outcome == 3:
            return

        self.data['trials'][-1].update(dict(
            spout=self._current_spout,
            shaping=self._water_at_cue_onset,
            cue_duration=cue_duration * 1000,
            outcome=self._outcome,
            spout_position=self._spout_position,
        ))
        self._recent_trials.append(self.data['trials'][-1])

    def on_iti_lift(self, side):
        """
        To be executed when the inter-trial interval is broken when the mouse
        prematurely lifts either paw from the paw rests.

        Parameters
        ----------
        side : :class:`int`
            Which paw was lifted: 0 for left, 1 for right

        """
        self._iti_broken = True
        self.data['resets'].append((time.time(), side))

    def on_iti_grasp(self, side):
        """
        To be executed when a spontaneous reach is made during the inter-trial interval.

        Parameters
        ----------
        side : :class:`int`
            Which spout was grasped: 0 for left, 1 for right.

        """
        self.data['spontaneous_reaches'].append((time.time(), side))
        self._message('Spontaneous reach made!')

    def on_trial_lift(self, side):
        """
        To be executed when the first paw lift occurs during each trial.

        Parameters
        ----------
        side : :class:`int`
            Which spout side paw was lifted: 0 for left, 1 for right.

        """
        if 'lift_time' not in self.data['trials'][-1]:
            self.data['trials'][-1]['lift_time'] = time.time()
            self.data['trials'][-1]['lift_paw'] = side

    def on_trial_correct(self):
        """
        To be executed upon successful grasp of the reach target during each trial.
        """
        self.data['trials'][-1]['end'] = time.time()
        self._backend.end_trial()
        self._outcome = 1
        if not self._water_at_cue_onset:
            self._backend.dispense_water(self._current_spout)

    def on_trial_incorrect(self):
        """
        To be executed upon grasp of the incorrect reach target during each trial.
        """
        self.data['trials'][-1]['end'] = time.time()
        self._backend.end_trial()
        self._outcome = 2
        if self._water_at_cue_onset:
            self._backend.miss_trial()

    def reverse_shaping(self):
        """
        Can be assigned to a button to reverse the state of the shaping boolean i.e.
        switches water dispensing between cue onset and grasp for the next trial.
        """
        self._water_at_cue_onset = not self._water_at_cue_onset
        self._message(f'Water at cue onset: {self._water_at_cue_onset}')

    def extend_trial(self):
        """
        Can be assigned to a button to stop the next trial from timing out, instead
        leaving the cue illuminated until grasped.
        """
        if self._extended_trial:
            self._extended_trial = False
            self._message('Next trial will NOT be an extended trial')
        else:
            self._extended_trial = True
            self._message('Next trial will be an extended trial')

    def _end_session(self, signal_number=None, frame=None):  # pylint: disable=W0613
        """
        End the current training session: uninitialise the raspberry pi, organise
        collected data, and display final training results. This also function serves as
        the main session Ctrl-C signal handler.

        Parameters
        ----------
        signal_number : :class:`int`, optional
            Passed to function by signal.signal; ignored.

        frame : :class:`int`, optional
            Passed to function by signal.signal; ignored.

        """
        if self._outcome == 3:
            return

        self._message = print
        self._outcome = 3
        self._backend.cleanup()
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        data = self.data
        if signal_number:
            data['end_time'] = time.time()
            data['duration'] = data['end_time'] - data['start_time']
        data['date'] = time.strftime('%Y-%m-%d')
        data['start_time'] = time.strftime(
            '%H:%M:%S', time.localtime(data['start_time'])
        )
        data['end_time'] = time.strftime(
            '%H:%M:%S', time.localtime(data['end_time'])
        )

    @cache
    def outcomes(self):
        """
        Get a list containing the outcomes for all trials.
        """
        return list(i['outcome'] for i in self.data['trials'])

    @cache
    def reward_count(self):
        """
        Get the number of rewarded trials.
        """
        return self.outcomes.count(1)  # pylint: disable=no-member

    @cache
    def reaction_times(self):
        """
        List of reaction times for this training session.

        Returns
        -------
        :class:`list` of :class:`float`\s
            Chronological list of reaction times in milliseconds.

        """
        reaction_times = []
        for trial in self.data['trials']:
            if trial['outcome'] == 1:
                reaction_times.append(trial['end'] - trial['start'])
        return reaction_times


def print_results(session):
    """
    Print the results of a training session.
    """
    data = session.data

    if not data['trials']:
        return
    if 'outcome' not in data['trials'][-1]:
        data['trials'].pop()
        if not data['trials']:
            return

    trial_count = len(data['trials'])
    miss_count = session.outcomes.count(0)
    miss_perc = 100 * miss_count / trial_count
    reward_count = session.outcomes.count(1)
    reward_perc = 100 * reward_count / trial_count
    incorrect_count = session.outcomes.count(2)
    incorrect_perc = 100 * incorrect_count / trial_count
    reset_pins = [y for x, y in data['resets']]
    left_resets = reset_pins.count(0)
    right_resets = reset_pins.count(1)

    print(textwrap.dedent(f"""
        _________________________________
        # __________ The End __________ #

        Trials:            {trial_count}
        Correct reaches:   {reward_count} ({reward_perc:0.1f}%)
        Incorrect reaches: {incorrect_count} ({incorrect_perc:0.1f}%)
        Missed cues:       {miss_count} ({miss_perc:0.1f}%)
        Spont. reaches:    {len(data['spontaneous_reaches'])}
        ITI resets:        {len(data['resets'])}
            left paw:      {left_resets}
            right paw:     {right_resets}
        # _____________________________ #
    """))
