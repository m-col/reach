#!/usr/bin/env python3
"""
Example script plotting metrics to illustrate how well a cohort of mice are training
across days.
"""


import sys

import matplotlib.pyplot as plt
import seaborn as sns

from reach import Cohort


def main(cohort):
    fig, axes = plt.subplots(5, 1, sharex=True)

    sns.lineplot(
        data=cohort.results,
        x='day',
        y='trials',
        hue='mouse_id',
        legend=False,
        ax=axes[0],
    )

    sns.lineplot(
        data=cohort.results,
        x='day',
        y='correct',
        hue='mouse_id',
        legend=False,
        ax=axes[1],
    )

    sns.lineplot(
        data=cohort.results,
        x='day',
        y='hit_rate',
        hue='mouse_id',
        legend=False,
        ax=axes[2],
    )

    sns.lineplot(
        data=cohort.results,
        x='day',
        y='incorrect',
        hue='mouse_id',
        legend=False,
        ax=axes[3],
    )

    sns.lineplot(
        data=cohort.trials,
        x='day',
        y='spout_position',
        hue='mouse_id',
        legend=False,
        ax=axes[4],
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
