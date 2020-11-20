#!/usr/bin/env python3
"""
Example script for plotting reaction times across all sessions for a cohort of mice.
"""


import os

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import pandas as pd

from reach import Cohort
from reach.session import Outcomes


def main(cohort):
    mouse = 0
    trials = pd.DataFrame(cohort.get_trials())
    trials["reaction_time"] = trials.end - trials.start
    trials.loc[trials["outcome"] == Outcomes.MISSED, "reaction_time"] = np.nan
    trials.loc[trials["outcome"] == Outcomes.CANCELLED, "reaction_time"] = np.nan

    sns.stripplot(
        data=trials,
        x='day',
        y='reaction_time',
        hue='mouse_id',
        dodge=True,
    )

    plt.show()


if __name__ == '__main__':
    mouse_ids = []
    for i in sys.argv[2:]:
        mouse_ids.append(i)
    if not mouse_ids:
        raise SystemError(
            f'Usage: {__file__} /path/to/json/folder mouse1 mouse2'
        )

    cohort = Cohort.init_from_files(
        data_dir=sys.argv[1],
        mouse_ids=mouse_ids,
    )

    main(cohort)
