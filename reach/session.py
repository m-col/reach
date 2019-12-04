"""
Sessions
========

:class:`.Session` objects interface with a raspberry pi to sequence training sessions
and record data.

"""
# pylint: disable=unused-argument


import json
import random
import signal
import sys
import textwrap
import time

from collections import deque
from reach.curses import RPiCurses
from reach.raspberry import RPi
from reach.utilities import enforce_suffix, lazy_property


# Number of recent trials used to calculate adaptive task settings
_SLIDING_WINDOW = 10


class Session:
    """
    Controls a single training session and its behavioural data.

    Attributes
    ----------
    data : :class:`dict`
        Stores all training data that is saved and loaded from the training JSONs. Can
        be passed as a kwarg to pre-fill entries.

    reward_count : int
        The number of rewarded trials in this session. This is exposed so scripts can
        calculate and display how much water to give a mouse after a session.

    """

    def __init__(self, data=None):
        """
        Instantiate a representation of a training session.
        """
        self.data = {}
        if data is not None:
            self.data.update(data)

        # These attributes track state during training
        self.reward_count = 0
        self._outcome = 0
        self._iti_broken = False
        self._current_spout = None
        self._water_at_cue_onset = None
        self._rpi = None
        self._message = print
        self._extended_trial = False
        self._cue_duration = 10000
        self._recent_trials = deque([], _SLIDING_WINDOW)

    @classmethod
    def init_all_from_file(cls, json_path=None):
        """
        Generate a :class:`list` of :class:`Session` objects from data stored in a
        Training JSON.

        Parameters
        ----------
        json_path : :class:`str`
            Training JSON to read data from.

        """
        json_path = enforce_suffix(json_path, '.json')

        with open(json_path, 'r') as json_file:
            file_data = json.load(json_file)

        training_data = [
            cls(data=session_data) for session_data in file_data
        ]

        return training_data

    def run(self, config, prev_data=None, curses=False):
        """
        Begin a training session.

        Parameters
        ----------
        config : :class:`dict`
            Training settings.

        prev_data : :class:`dict` of :class:`reach.Session` data
            Training data from the previous session, which if provided will be used when
            calculating initial cue duration, spout position and shaping status.

        curses: :class:`bool` (optional)
            Specify whether to use curses interface, and therefore mock raspberry pi,
            for a test training session.

        """
        random.seed()

        data = self.data
        data.update(config)
        data['trials'] = []
        data['resets'] = []
        data['spontaneous_reaches'] = []

        if curses:
            self._rpi = RPiCurses(data['spout_count'])
            self._message = self._rpi.print_to_feed
        else:
            self._rpi = RPi(data['spout_count'])

        self._display_training_settings()

        if prev_data:
            num_recent_trials = min(len(prev_data['trials']), _SLIDING_WINDOW)
            self._recent_trials.extend(prev_data['trials'][- num_recent_trials:])
            self._rpi.spout_position = self._recent_trials[-1]['spout_position']
        else:
            self._rpi.spout_position = 0

        if not self._rpi.wait_to_start():
            # Control-C hit while waiting.
            self._rpi.cleanup()
            print('Cancelled..')
            sys.exit(1)

        self._rpi.hold_spouts()
        signal.signal(signal.SIGINT, self._end_session)
        self._trial_loop()
        self._end_session()

    def _display_training_settings(self):
        """
        Display the training settings that will be used for the upcoming training
        session.
        """
        iti_min, iti_max = self.data['iti']

        self._message(textwrap.dedent(
            f"""
            _________________________________

            Spouts:      {self.data['spout_count']}
            Duration:    {self.data['duration']} s
            ITI:         {iti_min} - {iti_max} ms
            _________________________________

            """
        ))

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
            self._adapt_settings()

            self._message("_____________________________________")
            self._message("# -- Starting trial #%i -- %4.0f s -- #"
                          % (trial_count, now - data['start_time']))

            self._current_spout = random.randint(0, data['spout_count'] - 1)
            if self._inter_trial_interval():
                self._trial()
                self._message(f"Total rewards: {self.reward_count}")
                now = time.time()

            if self._outcome == 3:
                break

    def _inter_trial_interval(self):
        """
        Run inter-trial interval during training session.

        During the inter-trial interval we start listening for mouse movements using the
        touch sensors. Shaping can be toggled by pressing the start button.
        """
        self._rpi.monitor_sensors(
            self._reset_iti_callback,
            self._increase_spont_reaches_callback,
        )
        self._rpi.set_button_callback(0, self._reverse_shaping_callback)
        self._rpi.set_button_callback(1, self._extend_trial)
        self._extended_trial = False

        self._iti_broken = True
        while self._iti_broken:
            self._rpi.wait_for_rest()
            self._iti_broken = False

            now = time.time()
            iti_duration = random.uniform(*self.data['iti']) / 1000
            trial_end = now + iti_duration
            self._message(f"Counting down {iti_duration:.2f}s")

            while now < trial_end and not self._iti_broken:
                if self._outcome == 3:
                    return False
                time.sleep(0.020)
                now = time.time()

        self._rpi.disable_callbacks()
        return True

    def _reset_iti_callback(self, pin):
        """
        Callback function executed when the inter-trial interval is broken when
        the mouse prematurely lifts either paw from the paw rests.

        Parameters
        ----------
        pin : int
            Pin number listening to the touch sensor that detected the
            movement.

        """
        self._iti_broken = True
        self.data['resets'].append(
            (time.time(), self._rpi.paw_pins.index(pin))
        )

    def _increase_spont_reaches_callback(self, pin):
        """
        Callback function executed when a spontaneous reach is made during the
        inter-trial interval.

        Parameters
        ----------
        pin : int
            Pin number listening to the touch sensor that detected the
            spontaneous reach.

        """
        self.data['spontaneous_reaches'].append(
            (time.time(), 0 if self._rpi.spouts[0].touch else 1)
        )
        self._message('Spontaneous reach made!')

    def _reverse_shaping_callback(self, pin):
        """
        Callback function applied to start button that reverses the state of
        the shaping boolean i.e. switches water dispensing between cue onset
        and grasp for the next trial.

        Parameters
        ----------
        pin : int
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self._water_at_cue_onset = not self._water_at_cue_onset
        self._message(f'Water at cue onset: {str(self._water_at_cue_onset)}')

    def _trial(self):
        """
        Run trial during training session.
        """
        current_spout = self._current_spout
        reward_duration = self.data['reward_duration_ms'][current_spout]
        self.data['trials'].append({})

        self._rpi.start_trial(
            current_spout,
            self._record_lift_timepoints,
            self._reward_callback,
            self._incorrect_grasp_callback,
        )

        if self._water_at_cue_onset:
            self._rpi.dispense_water(
                current_spout,
                reward_duration,
            )

        now = time.time()
        self.data['trials'][-1].update(dict(start=now))

        if self._extended_trial:
            cue_duration = self.data['end_time'] - now
        else:
            cue_duration = self._cue_duration / 1000
        cue_end = now + cue_duration

        while not self._outcome and now < cue_end:
            time.sleep(0.008)
            now = time.time()

        if self._outcome == 0:
            self._rpi.end_trial()
            self._rpi.miss_trial()
            self._message("Missed reach")

        elif self._outcome == 1:
            self._message("Successful reach!")
            self.reward_count += 1
            time.sleep(reward_duration / 1000)

        elif self._outcome == 2:
            self._message("Incorrect reach!")
            time.sleep(reward_duration / 1000)

        self.data['trials'][-1].update(dict(
            spout=current_spout,
            shaping=self._water_at_cue_onset,
            cue_duration=cue_duration,
            outcome=self._outcome,
            spout_position=self._rpi.spout_position,
        ))
        self._recent_trials.append(self.data['trials'][-1])

    def _record_lift_timepoints(self, pin):
        """
        Record timepoint of paw lifts during trials.

        Parameters
        ----------
        pin : int
            Pin number listening to the touch sensor that detected the
            movement.

        """
        if 'lift_time' not in self.data['trials'][-1]:
            self.data['trials'][-1]['lift_time'] = time.time()
            self.data['trials'][-1]['lift_paw'] = self._rpi.paw_pins.index(pin)

    def _reward_callback(self, pin):
        """
        Callback function executed upon successful grasp of illuminated reach
        target during trial.

        Parameters
        ----------
        pin : int
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self.data['trials'][-1]['end'] = time.time()
        self._rpi.end_trial()
        self._outcome = 1
        if not self._water_at_cue_onset:
            self._rpi.dispense_water(
                self._current_spout,
                self.data['reward_duration_ms'][self._current_spout],
            )

    def _incorrect_grasp_callback(self, pin):
        """
        Callback function executed upon grasp of incorrect reach target during
        trial.

        Parameters
        ----------
        pin : int
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self.data['trials'][-1]['end'] = time.time()
        self._rpi.end_trial()
        self._outcome = 2
        if self._water_at_cue_onset:
            self._rpi.miss_trial()

    def _extend_trial(self, pin):
        """
        Callback function assigned to a button that will stop the next trial from timing
        out, instead leaving the cue illuminated until grasped.
        """
        if self._extended_trial:
            self._extended_trial = False
            print('Next trial will NOT be an extended trial')
        else:
            self._extended_trial = True
            print('Next trial will be an extended trial')

    def _adapt_settings(self):
        """
        Adapt live training settings based on recent behavioural performance.
        """
        num_hits = len([x for x in self._recent_trials if x['outcome'] == 1])

        if num_hits == _SLIDING_WINDOW:
            self._water_at_cue_onset = False
        else:
            self._water_at_cue_onset = True
            self._message('Shaping.')

        if num_hits >= _SLIDING_WINDOW - 1:
            self._cue_duration *= 0.9

        if num_hits == _SLIDING_WINDOW:
            self._rpi.spout_position += 1
            print(f'Spouts moved to position {self._rpi.spout_position}')
            time.sleep(1)
            self._rpi.hold_spouts()
        elif num_hits < _SLIDING_WINDOW / 4 and self._rpi.spout_position > 1:
            self._rpi.spout_position -= 1
            print(f'Spouts moved to position {self._rpi.spout_position}')
            time.sleep(1)
            self._rpi.hold_spouts()

    def _end_session(self, signal_number=None, frame=None):
        """
        End the current training session: uninitialise the raspberry pi,
        organise collected data, and display final training results. This also
        function serves as the main session Ctrl-C signal handler.

        Parameters
        ----------
        signal_number : int, optional
            Passed to function by signal.signal; ignored.

        frame : int, optional
            Passed to function by signal.signal; ignored.

        """
        if self._outcome == 3:
            return

        self._message = print
        self._outcome = 3
        self._rpi.cleanup()
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

        self._display_training_results()

    def _display_training_results(self):
        """
        Print training results at the end of the session.
        """
        data = self.data
        trial_count = len(data['trials'])
        if trial_count == 0:
            return

        miss_count = trial_count - self.reward_count
        reward_perc = 100 * self.reward_count / trial_count
        miss_perc = 100 * miss_count / trial_count
        reset_pins = [y for x, y in data['resets']]
        left_resets = reset_pins.count(0)
        right_resets = reset_pins.count(1)

        self._message(textwrap.dedent(f"""
        _________________________________
        # __________ The End __________ #

        Trials:            {trial_count}
        Correct reaches:   {self.reward_count} ({reward_perc:0.1f}%)
        Missed cues:       {miss_count} ({miss_perc:0.1f}%)
        Spont. reaches:    {len(data['spontaneous_reaches'])}
        ITI resets:        {len(data['resets'])}
            left paw:      {left_resets}
            right paw:     {right_resets}
        # _____________________________ #
        """))

    def add_training_notes(self):
        """
        Add arbitrary training notes to this session's data dictionary.
        """

        self._message('Add any notes to save:')
        self.data["notes"] = input()

    @lazy_property
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
