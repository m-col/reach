#!/usr/bin/env python3
"""
Example script for plotting reaction times across all sessions for a cohort of mice.
"""


import os

import matplotlib.pyplot as plt
import seaborn as sns
import sys
import pandas as pd

from reach import Cohort


def main(cohort):
    mouse = 0
    rts = pd.DataFrame(cohort.mice[mouse].reaction_times).transpose()

    sns.stripplot(
        data=cohort.trials,
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
