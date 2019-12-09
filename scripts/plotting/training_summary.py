#!/usr/bin/env python3
"""
Example script for plotting reaction times across all sessions for a cohort of
mice.
"""


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from reach import Cohort


mouse_ids = []
for i in sys.argv[1:]:
    mouse_ids.append(i)
if not mouse_ids:
    raise SystemError('Pass mouse IDs as args')


cohort = Cohort.init_from_files(
    json_path='/mnt/ardbeg/CuedBehaviourAnalysis/Data/TrainingJSON',
)

fig, axes = plt.subplots(4, 1, sharex=False)

sns.lineplot(
    data=cohort.trials,
    x='day',
    y='start',
    hue='mouse',
    ax=axes[0]
)

sns.lineplot(
    data=cohort.trials,
    x='day',
    y='spout_position',
    hue='mouse',
    ax=axes[1]
)

sns.lineplot(
    data=cohort.trials,
    x='day',
    y='spout_position',
    hue='mouse',
    ax=axes[2]
)

sns.lineplot(
    data=cohort.trials,
    x='day',
    y='spout_position',
    hue='mouse',
    ax=axes[3]
)

plt.show()
