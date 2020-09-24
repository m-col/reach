#!/usr/bin/env python3
"""
Example script plotting metrics to illustrate how well a cohort of mice are training
across days.
"""


import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from reach import Cohort


def main(cohort):
    fig, axes = plt.subplots(6, 1, sharex=True)

    results = pd.DataFrame()
    for mouse in cohort.results:
        results = results.append(pd.DataFrame(mouse))

    sns.lineplot(
        data=results,
        x='day',
        y='trials',
        hue='mouse_id',
        legend='brief',
        ax=axes[0],
    )
    axes[0].set_ylim(bottom=0)
    axes[0].set_ylabel('No.\ntrials', rotation="horizontal", ha="right")

    sns.lineplot(
        data=results,
        x='day',
        y='correct',
        hue='mouse_id',
        legend=False,
        ax=axes[1],
    )
    axes[1].set_ylim(bottom=0)
    axes[1].set_ylabel('No.\ncorrect', rotation="horizontal", ha="right")

    results['Hit rate'] = results['correct'] / results['trials']
    sns.lineplot(
        data=results,
        x='day',
        y='Hit rate',
        hue='mouse_id',
        legend=False,
        ax=axes[2],
    )
    axes[2].set_ylim(bottom=0, top=1)
    axes[2].set_ylabel('Hit rate', rotation="horizontal", ha="right")

    sns.lineplot(
        data=results,
        x='day',
        y='incorrect',
        hue='mouse_id',
        legend=False,
        ax=axes[3],
    )
    axes[3].set_ylim(bottom=0)
    axes[3].set_ylabel('No.\nincorrect', rotation="horizontal", ha="right")

    axes[4].axhline(0, color='#aaa', alpha=0.5, ls='--')
    # 1.5 here is an arbitrary threshold of ability to discriminate
    axes[4].axhline(1.5, color='#aaa', alpha=0.5, ls=':')
    sns.lineplot(
        data=results,
        x='day',
        y='d_prime',
        hue='mouse_id',
        legend=False,
        ax=axes[4],
    )
    axes[4].set_ylim(top=2)
    axes[4].set_ylabel("d'", rotation="horizontal", ha="right")

    axes[5].axhline(7, color='#aaa', alpha=0.5, ls='--')
    sns.lineplot(
        data=cohort.trials,
        x='day',
        y='spout_position',
        hue='mouse_id',
        legend=False,
        ax=axes[5],
    )
    axes[5].set_ylim(bottom=0, top=8)
    axes[5].set_ylabel('Spout\nposition\n(mm)', rotation="horizontal", ha="right")

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
