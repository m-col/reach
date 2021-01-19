#!/usr/bin/env python3
"""
Example script plotting metrics to illustrate how well a cohort of mice are training
across days.

Usage:
training_summary.py /path/to/data_dir mouse1 mouse2 ...

"""

import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MultipleLocator

from reach import Cohort


def main(cohort):
    sns.set_style("darkgrid")
    results = pd.DataFrame(cohort.get_results())
    trials = pd.DataFrame(cohort.get_trials())


    results.loc[
        results["trials"] == 0, ["correct", "incorrect", "d_prime", "trials"]
    ] = np.nan
    results.loc[results["single_spout"], "d_prime"] = np.nan


    # This makes the lines appear to "break" at changes between headfixed or
    # freely-moving days
    results["headfixed"] = results["training_box"]
    results.loc[results["headfixed"].str.startswith("fm"), "headfixed"] = 0
    results.loc[results["headfixed"] != 0, "headfixed"] = 1
    results_hf = results.copy()
    cols = ['trials', 'missed', 'correct', 'incorrect', 'd_prime']
    results_hf.loc[results["headfixed"] == 0, cols] = np.nan
    results.loc[results["headfixed"] == 1, cols] = np.nan
    results_hf.headfixed = 1
    results.headfixed = 0
    results = results.append(results_hf)


    # If all mice were single-spout only then we don't plot incorrects or d'
    if results.single_spout.all():
        plots = 4
    else:
        plots = 6
    _, axes = plt.subplots(plots, 1, sharex=True)


    # Number of trials
    sns.lineplot(
        data=results, x='day', y='trials', hue='mouse_id', legend='brief', ax=axes[0],
        style="headfixed", markers=True
    )
    axes[0].set_ylabel('No.\ntrials', rotation="horizontal", ha="right")
    axes[0].set_ylim(bottom=0)


    # Number of correct trials
    sns.lineplot(
        data=results, x='day', y='correct', hue='mouse_id', legend=False, ax=axes[1],
        style="headfixed", markers=True,
    )
    axes[1].set_ylabel('No.\ncorrect', rotation="horizontal", ha="right")


    # Hit rate
    results['Hit rate'] = results['correct'] / results['trials']
    sns.lineplot(
        data=results, x='day', y='Hit rate', hue='mouse_id', legend=False, ax=axes[2],
        style="headfixed", markers=True,
    )
    axes[2].set_ylabel('Hit rate', rotation="horizontal", ha="right")


    if plots == 6:
        # Number of incorrect trials
        sns.lineplot(
            data=results, x='day', y='incorrect', hue='mouse_id', legend=False,
            ax=axes[3], style="headfixed", markers=True,
        )
        axes[3].set_ylabel('No.\nincorrect', rotation="horizontal", ha="right")


        # d'
        axes[4].axhline(0, color='#aaaaaa', alpha=0.5, ls='--')
        # 1.5 here is an arbitrary threshold of ability to discriminate
        axes[4].axhline(1.5, color='#aaaaaa', alpha=0.5, ls=':')
        sns.lineplot(
            data=results, x='day', y='d_prime', hue='mouse_id', legend=False,
            ax=axes[4], style="headfixed", markers=True,
        )
        axes[4].set_ylabel("d'", rotation="horizontal", ha="right")


    # Spout position
    axes[-1].axhline(7, color='#aaaaaa', alpha=0.5, ls='--')
    sns.lineplot(
        data=trials, x='day', y='spout_position', hue='mouse_id', legend=False,
        ax=axes[-1], markers=True,
    )
    axes[-1].set_ylim(bottom=0, top=8)
    axes[-1].set_ylabel('Spout\nposition\n(mm)', rotation="horizontal", ha="right")

    axes[-1].xaxis.set_major_locator(MultipleLocator(2))
    plt.suptitle("Training summary for mice: " + ', '.join(cohort.mouse_ids))
    plt.show()


if __name__ == '__main__':
    mouse_ids = []
    for i in sys.argv[2:]:
        mouse_ids.append(i)
    if not mouse_ids:
        raise SystemError(
            f'Usage: {__file__} /path/to/data_dir mouse1 mouse2'
        )

    cohort = Cohort.init_from_files(
        data_dir=sys.argv[1],
        mouse_ids=mouse_ids,
    )

    main(cohort)
    raise Exception
