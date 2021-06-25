"""
Sessions
========

:class:`Session` objects interface with a backend such as a raspberry pi to operate
training sessions and record data.
"""

import json
import random
import signal
import time
from collections import deque
from statistics import NormalDist

import reach.backends

settings_fstring = """
_________________________________

Duration:               {duration} s
Inter-trial interval:   {iti_min} - {iti_max} ms
Initial cue duration:   {cue_duration} ms
Initial spout position: {spout_position}
Timeout penalty:        {timeout} ms
_________________________________
"""

results_fstring = """
_________________________________
# __________ The End __________ #

Trials:            {trial_count}
Correct reaches:   {reward_count} ({reward_perc:0.1f}%)
Incorrect reaches: {incorrect_count} ({incorrect_perc:0.1f}%)
d'                 {d_prime}
Missed cues:       {miss_count} ({miss_perc:0.1f}%)
Spont. reaches:    {spont_count}
ITI resets:        {reset_count}
    left paw:      {left_resets}
    right paw:     {right_resets}
# _____________________________ #
"""


class Outcomes:
    """
    These values label all possible trial outcomes.
    """
    TBD = 0
    MISSED = 0
    CORRECT = 1
    INCORRECT = 2
    CANCELLED = 3


class Targets:
    """
    These represent the 2 target positions.
    """
    LEFT = 0
    RIGHT = 1


class SlidingTrialList(deque):
    """
    A list of fixed length self.WINDOW, the number of recent trials used to calculate
    adaptive task settings for upcoming trials.
    """
    WINDOW = 15

    def __init__(self):
        deque.__init__(self, [], self.WINDOW)

    def get_hit_rate(self):
        """
        Return the proportion of trials in the sliding window that were successful.
        """
        num_hits = len([i for i in self if i['outcome'] == Outcomes.CORRECT])
        return num_hits / self.WINDOW

    def get_touch_rate(self):
        """
        Return the proportion of trials in the sliding window that resulted in reaches,
        whether correct or incorrect.
        """
        num_hits = 0
        for i in self:
            if i['outcome'] == Outcomes.CORRECT or i['outcome'] == Outcomes.INCORRECT:
                num_hits += 1
        return num_hits / self.WINDOW


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
        self._recent_trials = [SlidingTrialList(), SlidingTrialList()]
        self._reward_count = 0
        self._outcome = Outcomes.TBD
        self._iti_broken = False
        self._current_spout = Targets.LEFT
        self._backend = None
        self._message = print
        self._cue_duration = 10000
        self._spout_position = [1, 1]
        self._advance_delay = 1
        self._hook = None

    @classmethod
    def init_all_from_file(cls, data_file):
        """
        Generate a :class:`list` of :class:`Session` objects from data stored in a
        Training JSON.

        Parameters
        ----------
        data_file : :class:`str`
            Full path to file containing existing training data.

        Returns
        -------
        :class:`list`
            List of :class:`Session` instances.

        """
        with open(data_file, "r") as fd:
            previous_data = json.load(fd)

        return [cls(data=data) for data in previous_data]

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
        hook=None,
        timeout=None,
        initial_spout=None,
        advance_with_incorrects=False,
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
            calculating initial cue duration and spout position.

        hook : :class:`callable`, optional
            An object that will be called at the end of every trial.

        timeout : :class:`int`, optional
            Duration in milliseconds of a timeout to wait after an incorrect trial.

        initial_spout : :class:`int`, optional
            Initial spout to use for session. Default: None; initial spout is randomly
            selected.

        advance_with_incorrects : :class:`bool`, optional
            If True, advancements between trials in spout position and cue duration can
            happen as long as the mouse is touch any reach target consistently, rather
            than reaching only to the current target.

        """
        if not isinstance(backend, reach.backends.Backend):
            raise TypeError("Provided backend is not an instance of reach.backend.Backend")

        self._backend = backend
        self._hook = hook

        if hasattr(self._backend, "message"):
            self._message = self._backend.message

        self.data["duration"] = duration or 1800
        self.data["timeout"] = timeout or 8000
        self.data["intertrial_interval"] = intertrial_interval or (4000, 6000)
        self.data["trials"] = []
        self.data["resets"] = []
        self.data["spontaneous_reaches"] = []
        self.data["advance_with_incorrects"] = advance_with_incorrects

        if previous_data and previous_data["trials"]:
            prev_left = [
                t for t in previous_data["trials"] if t.get("spout") == Targets.LEFT
            ]
            prev_right = [
                t for t in previous_data["trials"] if t.get("spout") == Targets.RIGHT
            ]
            self._recent_trials[Targets.LEFT].extend(prev_left)
            self._recent_trials[Targets.RIGHT].extend(prev_right)
            self._spout_position = previous_data["trials"][-1]["spout_position"]

            try:
                self._cue_duration = min(
                    self._recent_trials[Targets.LEFT][-1]["cue_duration"],
                    self._recent_trials[Targets.RIGHT][-1]["cue_duration"],
                )
            except IndexError:
                pass

        if initial_spout is None:
            self._current_spout = random.randint(Targets.LEFT, Targets.RIGHT)
        else:
            self._current_spout = initial_spout

        self._backend.position_spouts(self._spout_position)
        self._display_training_settings()
        self._backend.configure_callbacks(self)

        try:
            self._backend.wait_to_start()
        except KeyboardInterrupt:
            self._backend.cleanup()
            self._message("Cancelled..")
            return

        signal.signal(signal.SIGINT, self._end_session)
        self._trial_loop()
        self._end_session()

    def _display_training_settings(self):
        """
        Display the training settings that will be used for the upcoming training
        session.
        """
        iti_min, iti_max = self.data["intertrial_interval"]

        self._message(settings_fstring.format(
            duration=self.data['duration'],
            iti_min=iti_min,
            iti_max=iti_max,
            cue_duration=self._cue_duration,
            spout_position=self._spout_position,
            timeout=self.data['timeout'],
        ))

    def _trial_loop(self):
        """
        Loop over the main event sequence forming the behavioural task.
        """
        data = self.data
        now = time.time()
        data["start_time"] = now
        data["end_time"] = now + data["duration"]
        trial_count = 0

        while now < data["end_time"]:
            trial_count += 1
            self._outcome = Outcomes.TBD
            self._message("_____________________________________")
            self._message(
                "# -- Starting trial #%i -- %4.0f s -- #"
                % (trial_count, now - data["start_time"])
            )
            self._adapt_settings()
            if self._hook is not None:
                self._hook()
            if self._inter_trial_interval():
                self._trial()
                self._message(f"Total rewards: {self._reward_count}")
                now = time.time()

            if self._outcome == Outcomes.CANCELLED:
                break

    def _adapt_settings(self):
        """
        Adapt live training settings based on recent behavioural performance.
        """
        self._advance_delay -= 1

        advance = False
        if self.data["advance_with_incorrects"]:
            advance = self._recent_trials[self._current_spout].get_touch_rate() >= 0.90
        else:
            advance = self._recent_trials[self._current_spout].get_hit_rate() >= 0.90

        if advance and self._advance_delay <= 0:
            self._advance_delay = 5
            other_spout = abs(self._current_spout - 1)
            if self._spout_position[self._current_spout] < 7:
                self._spout_position[self._current_spout] += 1
                self._backend.position_spouts(self._spout_position)
                self._message(f"Spouts progressed to position {self._spout_position}")

            elif self._spout_position[other_spout] < 7:
                self._spout_position[other_spout] += 1
                self._backend.position_spouts(self._spout_position)
                self._message(f"Spouts progressed to position {self._spout_position}")

            elif self._cue_duration > 2000:
                self._cue_duration = max(int(self._cue_duration * 0.997), 2000)
                self._message(f"Cue duration decreased to {self._cue_duration} ms")

    def _inter_trial_interval(self):
        """
        Run inter-trial interval during training session.

        During the inter-trial interval we start listening for mouse movements using the
        touch sensors.

        Returns
        -------
        :class:`bool`
            Whether to ITI ended normally rather than due to a manual cancellation of
            the session.

        """
        self._backend.start_iti()
        self._iti_broken = True

        while self._iti_broken:
            if not self._backend.wait_for_rest():
                return False
            self._iti_broken = False

            now = time.time()
            iti_duration = random.uniform(*self.data["intertrial_interval"]) / 1000
            iti_end = now + iti_duration
            self._message(f"Counting down {iti_duration:.2f}s")

            while now < iti_end and not self._iti_broken:
                if self._outcome == Outcomes.CANCELLED:
                    return False
                time.sleep(0.020)
                now = time.time()

            if self._iti_broken:
                time.sleep(self.data["timeout"] / 1000)

        return True

    def _trial(self):
        """
        Run trial during training session.
        """
        now = time.time()
        self.data["trials"].append({"start": now})

        self._backend.start_trial(self._current_spout)

        cue_duration = self._cue_duration / 1000
        cue_end = now + cue_duration

        while not self._outcome and now < cue_end:
            time.sleep(0.008)
            now = time.time()

        if self._outcome == Outcomes.MISSED:
            self._backend.end_trial()
            self._backend.miss_trial()
            self._message("Missed reach")
            self.data["trials"][-1]["end"] = cue_end

        elif self._outcome == Outcomes.CORRECT:
            self._message("Successful reach!")
            self._reward_count += 1

        elif self._outcome == Outcomes.INCORRECT:
            self._message("Incorrect reach!")
            time.sleep(self.data["timeout"] / 1000)

        elif self._outcome == Outcomes.CANCELLED:
            return

        self.data["trials"][-1].update(
            dict(
                spout=self._current_spout,
                cue_duration=cue_duration * 1000,
                outcome=self._outcome,
                spout_position=self._spout_position,
            )
        )
        self._recent_trials[self._current_spout].append(self.data["trials"][-1])

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
        self.data["resets"].append((time.time(), side))

    def on_iti_grasp(self, side):
        """
        To be executed when a spontaneous reach is made during the inter-trial interval.

        Parameters
        ----------
        side : :class:`int`
            Which spout was grasped: 0 for left, 1 for right.

        """
        self._iti_broken = True
        self.data["spontaneous_reaches"].append((time.time(), side))
        self._message("Spontaneous reach made!")

    def on_trial_lift(self, side):
        """
        To be executed when the first paw lift occurs during each trial.

        Parameters
        ----------
        side : :class:`int`
            Which spout side paw was lifted: 0 for left, 1 for right.

        """
        if "lift_time" not in self.data["trials"][-1]:
            self.data["trials"][-1]["lift_time"] = time.time()
            self.data["trials"][-1]["lift_paw"] = side

    def on_trial_correct(self):
        """
        To be executed upon successful grasp of the reach target during each trial.
        """
        self.data["trials"][-1]["end"] = time.time()
        self._backend.end_trial()
        self._outcome = Outcomes.CORRECT
        self._backend.give_reward(self._current_spout)

    def on_trial_incorrect(self):
        """
        To be executed upon grasp of the incorrect reach target during each trial.
        """
        self.data["trials"][-1]["end"] = time.time()
        self._backend.end_trial()
        self._outcome = Outcomes.INCORRECT
        self._backend.miss_trial()

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
        if self._outcome == Outcomes.CANCELLED:
            return

        self._message = print
        self._outcome = Outcomes.CANCELLED
        self._backend.cleanup()
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        data = self.data
        data["end_time"] = time.time()
        data["duration"] = data["end_time"] - data["start_time"]
        data["date"] = time.strftime("%Y-%m-%d")

    def set_spout(self, spout):
        """
        Set the current spout for the next trial.

        Parameters
        ----------
        spout : :class:`int`
            The spout to use. If the value provided is -1, instead invert the
            choice from the current spout.

        """
        if spout == -1:
            self._current_spout = abs(self._current_spout - 1)
        else:
            self._current_spout = spout

    def get_recent_trials(self, spout=None):
        """
        Get last few trials that used a given spout.

        Parameters
        ----------
        spout : :class:`int`, optional
            The spout to get trials for. By default, get the recent trials for the
            current spout.

        """
        if spout is None:
            spout = self._current_spout
        return self._recent_trials[spout]

    def get_trials(self):
        """
        Get trial data for this session.

        Returns
        -------
        :class:`list` of :class:`dict`\s
            Chronological list of dicts, where each dict contains information about the
            nth trial.

        """
        if 'trials' in self.data:
            return self.data['trials'].copy()
        return None

    def get_d_prime(self):
        """
        Get the d' value for this session.

        d' is calculated as: d' = z(FA) - z(H)
        where "hits" (H) is success rate of left-target trials that involved reaching
        movements, and "false alarms" (FA) is incorrect rate of right-target trials that
        involved reaching movements. This metric does not account for miss trials where
        no reaches were made. A loglinear correction is used to account for extreme
        values (Hautus, 1995).

        """
        def z(p):
            return - NormalDist().inv_cdf(p)

        lefts = []
        rights = []
        for trial in self.data['trials']:
            outcome = trial.get("outcome")
            if outcome in (Outcomes.CORRECT, Outcomes.INCORRECT):
                if trial.get('spout') == Targets.LEFT:
                    lefts.append(outcome)
                else:
                    rights.append(outcome)

        H = (lefts.count(Outcomes.CORRECT) + 0.5) / (len(lefts) + 1)
        FA = (rights.count(Outcomes.INCORRECT) + 0.5) / (len(rights) + 1)
        d_prime = z(FA) - z(H)
        return d_prime

    def get_results(self):
        """
        Get the high-level results for this session.

        Returns
        -------
        :class:`dict`
            containing basic metrics of the session, and any other metadata found in
            :class:`Session.data`.

        """
        results = self.data.copy()
        trials = self.get_trials()
        if not trials:
            return None
        outcomes_l = [i["outcome"] for i in trials if 'spout' in i and i['spout'] == Targets.LEFT]
        outcomes_r = [i["outcome"] for i in trials if 'spout' in i and i['spout'] == Targets.RIGHT]
        results["missed_l"] = outcomes_l.count(Outcomes.MISSED)  # pylint: disable=E1101
        results["missed_r"] = outcomes_r.count(Outcomes.MISSED)  # pylint: disable=E1101
        results["correct_l"] = outcomes_l.count(Outcomes.CORRECT)  # pylint: disable=E1101
        results["correct_r"] = outcomes_r.count(Outcomes.CORRECT)  # pylint: disable=E1101
        results["incorrect_l"] = outcomes_l.count(Outcomes.INCORRECT)  # pylint: disable=E1101
        results["incorrect_r"] = outcomes_r.count(Outcomes.INCORRECT)  # pylint: disable=E1101
        results["trials"] = len(trials)
        results["resets"] = len(self.data["resets"])
        results["resets_l"] = len([x for x in self.data["resets"] if x[1] == Targets.LEFT])
        results["resets_r"] = len([x for x in self.data["resets"] if x[1] == Targets.RIGHT])
        results["spontaneous_reaches"] = len(self.data["spontaneous_reaches"])
        results["spontaneous_reaches_l"] = len(
            [x for x in self.data["spontaneous_reaches"] if x[1] == Targets.LEFT]
        )
        results["spontaneous_reaches_r"] = len(
            [x for x in self.data["spontaneous_reaches"] if x[1] == Targets.RIGHT]
        )
        results["d_prime"] = self.get_d_prime()
        return results

    def get_spontaneous_reaches(self):
        """
        Get the list of spontaneous reach timings and locations.

        Returns
        -------
        :class:`list`
            A list of (time, location) tuples, where location is equal to Targets.LEFT
            or Targets.RIGHT.

        """
        return [dict(timing=t, location=l) for t, l in self.data["spontaneous_reaches"]]


def print_results(session):
    """
    Print the results of a training session.
    """
    data = session.data
    trials = session.get_trials()

    if not trials:
        return
    if "outcome" not in trials[-1]:
        trials.pop()
        if not trials:
            return

    outcomes = [i.get("outcome") for i in trials]
    trial_count = len(trials)
    reward_count = outcomes.count(Outcomes.CORRECT)
    incorrect_count = outcomes.count(Outcomes.INCORRECT)
    miss_count = outcomes.count(Outcomes.MISSED)
    reset_pins = [y for x, y in data["resets"]]

    print(results_fstring.format(
        trial_count=trial_count,
        reward_count=reward_count,
        reward_perc=100 * reward_count / trial_count,
        incorrect_count=incorrect_count,
        incorrect_perc=100 * incorrect_count / trial_count,
        d_prime=session.get_d_prime(),
        miss_count=miss_count,
        miss_perc=100 * miss_count / trial_count,
        spont_count=len(data['spontaneous_reaches']),
        reset_count=len(data['resets']),
        left_resets=reset_pins.count(Targets.LEFT),
        right_resets=reset_pins.count(Targets.RIGHT),
    ))
