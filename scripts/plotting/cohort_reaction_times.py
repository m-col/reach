#!/usr/bin/env python3
"""
Plot reaction times across all sessions for a cohort of mice
"""


import os
import matplotlib.pyplot as plt
import seaborn as sns

from reach import Cohort


home = os.path.expanduser('~')
json_path = home + '/work/analysis/CuedBehaviourAnalysis/Data/TrainingJSON/'

mouse_ids = [
    'ImALM1',
    'ImALM2',
]

cohort = Cohort.init_from_files(
    mouse_ids=mouse_ids,
    json_path=json_path
)

import cProfile
cProfile.run('cohort.mice[1].reaction_times')
cProfile.run('cohort.mice[1].reaction_times')

#rts = cohort.mice[1].reaction_times
#
#sns.boxplot(
#    x="Session",
#    y="Reaction time",
#    data=rts,
#    #whis=np.inf,
#)

#sns.stripplot(
#    x="tip",
#    y="day",
#    data=tips,
#    jitter=True,
#    color=".3",
#)

plt.show()
