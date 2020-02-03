#!/usr/bin/env python3
"""
Example script for plotting reaction times across all sessions for a cohort of
mice.
"""


import os
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import pandas as pd

from reach import Cohort


# folder containing training data
json_path = '/mnt/ardbeg/CuedBehaviourAnalysis/Data/TrainingJSON'

# mice in cohort
mouse_ids = []
for i in sys.argv[1:]:
    mouse_ids.append(i)
if not mouse_ids:
    raise SystemError('Pass mouse IDs as args')

# load data
cohort = Cohort.init_from_files(
    mouse_ids=mouse_ids,
    json_path=json_path,
)

# plot  TODO: plot mice all together
mouse = 0
rts = pd.DataFrame(cohort.mice[mouse].reaction_times).transpose()

sns.violinplot(
    cut=0,
    data=rts,
    scale='area',
    inner='point',
)

plt.show()
