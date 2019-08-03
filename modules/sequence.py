#!/usr/bin/env python3



class Data(object):
    """ Store and manipulate behavioural data during training session """

    def __init__(self, spouts):
        """ Initialise data structure """
        # paw rest touch sensors
        self.lift       = []
        self.rest       = []
        self.grab       = []
        self.release    = []

    def reformat(self, p, spouts, sponts):
        """ Re-format the data for saving """
        # get data from each spout
        cue = []
        touch = []
        release = []
        for i in range(len(spouts)):
            cue.append(spouts[i].t_cue)
            touch.append(spouts[i].t_touch)
            release.append(spouts[i].t_release)

        self.cue = cue
        self.touch = touch
        self.release = release

        # get paw sensor data
        lift_l
        lift_r
        rest_l
        rest_r

