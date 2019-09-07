"""
Sessions
========

:class:`.Session` objects interface with a raspberry pi to sequence training
sessions and record data.

"""


import json
import random
import signal
import time

from reach.raspberry import _RPi


class Session:
    """
    Controls a single training session and its behavioural data.

    Attributes
    ----------
    data : :class:`dict`
        Stores all training data and metadata that is saved and loaded from the
        training JSONs. It can be specified as a kwarg to substantiate a past
        training session. See below for information on keys.

    data keys
    ---------
    spont_reach_spouts : :class:`list` of :class:`ints`
        During training this stores pin numbers corresponding to spout touch
        sensors that detect spontaneous reaches during the inter-trial
        interval, then at the end of training this is converted to 0s and 1s to
        represent left or right spout.

    spont_reach_timepoints : :class:`list` of :class:`ints`
        This contains the timepoints for all spontaneous reaches.

    resets_paw : :class:`list` of :class:`ints`
        During training this stores pin numbers corresponding to paw touch
        sensors that detect premature movements during the inter-trial
        interval, then at the end of training this is converted to 0s and 1s to
        represent left or right paws.

    resets_timepoints : :class:`list` of :class:`ints`
        This contains the timepoints for all premature movements that reset the
        inter-trial interval.

    """

    def __init__(self, data=None):
        if data is None:
            data = {}
            data['spont_reach_spouts'] = []
            data['spont_reach_timepoints'] = []
            data['resets_paw'] = []
            data['resets_timepoints'] = []
        else:
            self.data = data

    @classmethod
    def _init_all_from_file(cls, json_path):
        """
        Generate list of Session objects from data stored in Training JSON.

        Parameters
        ----------
        json_path : :class:`str`
            Training JSON to read data from.

        """
        with open(json_path, 'r') as json_file:
            file_data = json.load(json_file)

        training_data = [
            cls(data=session_data) for session_data in file_data
        ]

        return training_data
        

    def run(self, config):
        """
        Begin a training session.

        Parameters
        ----------
        config : :class:`dict`
            List of configuration parameters.

        Attributes
        ----------
        _outcome : :class:`int`
            State of current trial. 0 means non-action, 1 means success, 2
            means incorrect reach made.

        _iti_broken : :class:`bool`
            State of an inter-trial interval i.e. broken or not. This is
            updated upon internally-generated movement to reset the ITI.

        _current_spout : :class:`int`
            The spout number used for the current trial.

        _water_at_cue_onset : :class:`bool`
            Determines whether water will be dispensed at the next cue onset.

        _rpi : :class:`.RPi`
            The raspberry pi that controls the training box hardware.
        """

        random.seed()

        data = self.data
        data.update(config)

        self._outcome = 0
        self._iti_broken = False
        self._current_spout = None
        self._water_at_cue_onset = data['shaping']

        self._display_training_settings()

        self._rpi = _RPi._init_with_library_check(data['spout_count'])
        self._rpi._wait_to_start()

        signal.signal(
            signal.SIGINT,
            self._end_session_manually
        )

        now = time.time()
        data['start_time'] = now
        data['end_time'] = now + data['duration']

        trial_count = 0
        self._reward_count = 0

        while now < data['end_time']:
            trial_count += 1
            self._outcome = 0

            print("_________________________________________")
            print("# ---- Starting trial #%i -- %4.0f s ---- #"
                  % (trial_count, now - data['start_time']))

            self._current_spout = random.randint(0, data['spout_count'] - 1)
            self._inter_trial_interval()
            self._trial()

            print(f"Total rewards: {self._reward_count}")
            now = time.time()

        self._end_session()

    def _display_training_settings(self):
        """
        Display the training settings that will be used for the upcoming
        training session.
        """
        data = self.data
        iti_min, iti_max = data['iti']

        print("\n_________________________________\n")
        print(f"Spouts:      {data['spout_count']}")
        print(f"Duration:    {data['duration']} s")
        print(f"Cue:         {data['cue_duration_ms']} ms")
        print(f"ITI:         {iti_min} - {iti_max} ms")
        print(f"Shaping:     {data['shaping']}")
        print("\n_________________________________\n")

    def _inter_trial_interval(self):
        """
        Run inter-trial interval during training session.

        During the inter-trial interval we start listening for mouse movements
        using the touch sensors. Shaping can be toggled by pressing the start
        button.
        """
        self._rpi._monitor_sensors(
            self._current_spout,
            self._reset_iti_callback,
            self._increase_spont_reaches_callback
        )

        self._rpi._set_button_callback(self._reverse_shaping_callback)
        self._water_at_cue_onset = self.data['shaping']

        while True:
            self._rpi._wait_for_rest()
            self._iti_broken = False

            now = time.time()
            iti_duration = random.uniform(*self.data['iti']) / 1000
            trial_end = now + iti_duration
            print("Counting down {iti_duration:.2f}s")

            while now < trial_end and not self._iti_broken:
                time.sleep(0.020)
                now = time.time()

            if self._iti_broken:
                continue
            else:
                break

        self._rpi._disable_sensors()

    def _reset_iti_callback(self, pin):
        """
        Callback function executed when the inter-trial interval is broken when
        the mouse prematurely lifts either paw from the paw rests.

        Parameters
        ----------
        pin : :class:`int`
            Pin number listening to the touch sensor that detected the
            movement.
        """
        self._iti_broken = True
        self.data['resets_paws'].append(pin)
        self.data['resets_timepoints'].append(time.time())

    def _increase_spont_reaches_callback(self, pin):
        """
        Callback function executed when a spontaneous reach is made during the
        inter-trial interval.

        Parameters
        ----------
        pin : :class:`int`
            Pin number listening to the touch sensor that detected the
            spontaneous reach.
        """
        self.data['spont_reach_spouts'].append(pin)
        self.data['spont_reach_timepoints'].append(time.time())

    def _reverse_shaping_callback(self, pin):
        """
        Callback function applied to start button that reverses the state of
        the shaping boolean i.e. switches water dispensing between cue onset
        and grasp for the next trial.

        Parameters
        ----------
        pin : :class:`int`
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self._water_at_cue_onset = not self._water_at_cue_onset

    def _trial(self):
        """
        Run trial during training session.
        """
        current_spout = self._current_spout
        self._rpi._start_trial(
            current_spout,
            self._reward_callback,
            self._incorrect_grasp_callback
        )

        if self._water_at_cue_onset:
            self._rpi._dispense_water(current_spout, self.data['reward_duration_ms'])

        now = time.time()
        cue_end = now + self.data['cue_duration_ms'] / 1000

        while not self._outcome and now < cue_end:
            time.sleep(0.008)
            now = time.time()

        self._rpi._end_trial()

        if self._outcome == 1:
            print("Successful reach!")
            self._reward_count += 1
            time.sleep(self.data['reward_duration_ms'] / 1000)

        elif self._outcome == 2:
            print("Incorrect reach!")
            time.sleep(self.data['reward_duration_ms'] / 1000)

        else:
            print("Missed reach")

    def _reward_callback(self, pin):
        """
        Callback function executed upon successful grasp of illuminated reach
        target during trial.

        Parameters
        ----------
        pin : :class:`int`
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self._rpi._successful_grasp(self._current_spout)
        self._outcome = 1
        if not self._water_at_cue_onset:
            self._rpi._dispense_water(
                self._current_spout,
                self.data['reward_duration_ms']
            )

    def _incorrect_grasp_callback(self, pin):
        """
        Callback function executed upon grasp of incorrect reach target during
        trial.

        Parameters
        ----------
        pin : :class:`int`
            Passed to function by RPi.GPIO event callback; ignored.

        """
        self._rpi._incorrect_grasp(self._current_spout)
        self._outcome = 2

    def _end_session_manually(self, *args, **kwargs):
        """
        Control-C signal handler used during live training sessions that allows
        for clean exiting and saving of collected data.
        """
        print("\nExiting.")
        response = input("Do you want to keep collected data? (N/y) ")
        if response == "y":
            self._end_session(manual=True)

    def _end_session(self, manual=False):
        """
        End the current training session: uninitialise the raspberry pi GPIO
        pins, reorganise collected data, and display final training results.

        Parameters
        ----------
        manual : :class:`bool`, optional
            Specifies whether this function call was the result of a Ctrl-C
            press interrupting a training session.

        """
        self._rpi._cleanup()
        self._collate_data(manual=manual)
        self._display_training_results()
        print('\a')

    def _collate_data(self, manual=False):
        """
        Reorganise collected training data and metadata into the final form
        saved in training JSONs.

        Parameters
        ----------
        manual : :class:`bool`, optional
            Specifies whether the session was ended by a Ctrl-C press
            interrupting the training session.

        """
        data = self.data

        if manual:
            data['end_time'] = time.time()
            data['duration'] = data['end_time'] - data['start_time']

        data['cue_timepoints'] = []
        data['touch_timepoints'] = []

        for idx, spout in enumerate(self._rpi._spouts):
            data['spont_reach_spouts'] = map(
                lambda x: idx if x == spout['touch'] else x,
                data['spont_reach_spouts']
            )
            data['cue_timepoints'].append(spout['cue_timepoints'])
            data['touch_timepoints'].append(spout['touch_timepoints'])

        for idx, pin in enumerate(self._rpi._paw_pins):
            data['resets_paw'] = map(
                lambda x: idx if x == pin else x,
                data['resets_paw']
            )

        data['date'] = time.strftime('%Y-%m-%d')
        data['start_time'] = time.strftime(
            '%H:%M:%S', time.localtime(data['start_time'])
        )
        data['end_time'] = time.strftime(
            '%H:%M:%S', time.localtime(data['end_time'])
        )
        data["notes"] = input("\nAdd any notes to save:\n")

    def _display_training_results():
        """
        Print training results at the end of the session.
        """
        data = self.data
        trial_count = len(data['cue_timepoints']
        miss_count = trial_count - self._reward_count
        reward_perc = 100 * self._reward_count / trial_count
        miss_perc = 100 * miss_count / trial_count

        print("\n_________________________________\n")
        print("# __________ The End __________ #")
        print("")
        print("Trials:            {trial_count}")
        print("Rewarded reaches:  {self._reward_count} ({reward_perc:0.1f}%%)")
        print("Missed cues:       {miss_count} ({miss_perc:0.1f}%%)")
        print("Spont. reaches:    {len(data['spont_reach_spouts'])}")
        print("ITI resets:        {len(data['resets_paw'])}")
        print("    left paw:      {data['resets_paw'].count(0)}")
        print("    right paw:     {data['resets_paw'].count(1)}")
        print("\n# _____________________________ #\n")
        print("%i rewards * 6uL = %i uL")

    @property
    def reaction_times(self):
        """
        List of reaction times for this training session.

        Returns
        -------
        :class:`List` of :class:`Ints`s
            Chronological list of reaction times in milliseconds.
        """
        raise NotImplementedError
