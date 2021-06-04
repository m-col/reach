#!/usr/bin/env python3
"""
Example script for plotting reaction times across all sessions for a cohort of mice as a
lineplot of averages.
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
    trials = pd.DataFrame(cohort.get_trials())
    trials["reaction_time"] = trials.end - trials.start
    trials.loc[trials["outcome"] == Outcomes.MISSED, "reaction_time"] = np.nan
    trials.loc[trials["outcome"] == Outcomes.CANCELLED, "reaction_time"] = np.nan

    averages = {}
    for mouse in cohort:
        mouse_averages = trials.loc[trials["mouse_id"] == mouse.mouse_id].groupby('day').mean()
        mouse_averages = mouse_averages['reaction_time'].reset_index()
        averages[mouse.mouse_id] = pd.DataFrame(mouse_averages)

    df = pd.concat(averages)
    df.reset_index(inplace=True)

    sns.lineplot(
        data=df,
        x='day',
        y='reaction_time',
        hue='level_0',  # uncomment this to plot each mouse with its own line
    )
    plt.gca().set_ylim(bottom=0, top=10)

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
